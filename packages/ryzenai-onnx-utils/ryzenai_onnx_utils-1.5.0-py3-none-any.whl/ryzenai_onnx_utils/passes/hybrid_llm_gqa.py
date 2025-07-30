# Copyright (c) 2024 Advanced Micro Devices, Inc.

import contextlib

import numpy as np
import onnx

import ryzenai_onnx_utils.matcher


def concatenate_initializers(q_matmul, k_matmul, v_matmul, index, extractor):
    q_np = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
        q_matmul.input[index], extractor
    )
    k_np = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
        k_matmul.input[index], extractor
    )
    v_np = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
        v_matmul.input[index], extractor
    )

    qkv_np = np.concatenate((q_np, k_np, v_np), 0)
    qkv_np_name: str = q_matmul.input[index].replace("q_proj", "qkv_proj")
    qkv_np_name = qkv_np_name.replace("Add", "MatMulNBits")
    qkv_tensor = onnx.numpy_helper.from_array(qkv_np, qkv_np_name)
    tvi = onnx.helper.make_tensor_value_info(
        qkv_np_name, onnx.helper.np_dtype_to_tensor_dtype(qkv_np.dtype), qkv_np.shape
    )
    return qkv_tensor, tvi


def get_qkv_attribute(matmuls, attr_name, check_equal):
    """
    Go through the qkv matmuls and extract the attribute values. Check if they're
    equal, except for the case of N where we add them together

    Args:
        matmuls (list[NodeProto]): q, k, v matmuls
        attr_name (str): Name of the attribute to get
        check_equal (bool): Check if attribute value across matmuls are equal
    """
    attr_value = None
    for matmul in matmuls:
        if attr_value is None:
            attr_value = onnx.helper.get_node_attr_value(matmul, attr_name)
        else:
            new_value = onnx.helper.get_node_attr_value(matmul, attr_name)
            if check_equal:
                assert attr_value == new_value
            else:
                # for N
                attr_value += new_value
    return onnx.helper.make_attribute(attr_name, attr_value)


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    q_matmul = subgraph[0]
    k_matmul = subgraph[1]
    v_matmul = subgraph[2]
    q_rotary = subgraph[3]
    # k_rotary = subgraph[4]
    gqa = subgraph[5]

    # assuming matmulnbits have weights, scales, zero points and bias
    assert len(q_matmul.input) == len(k_matmul.input) == len(v_matmul.input)
    assert len(q_matmul.input) == 6
    has_bias = len(q_matmul.input) == 6
    assert q_matmul.input[0] == k_matmul.input[0] == v_matmul.input[0]

    qkv_weights_tensor, weights_tvi = concatenate_initializers(
        q_matmul, k_matmul, v_matmul, 1, extractor
    )
    qkv_scales_tensor, scales_tvi = concatenate_initializers(
        q_matmul, k_matmul, v_matmul, 2, extractor
    )
    qkv_zp_tensor, zp_tvi = concatenate_initializers(
        q_matmul, k_matmul, v_matmul, 3, extractor
    )

    new_nodes = []
    new_tvis = [weights_tvi, scales_tvi, zp_tvi]

    qkv_inputs = [
        q_matmul.input[0],
        qkv_weights_tensor.name,
        qkv_scales_tensor.name,
        qkv_zp_tensor.name,
    ]
    new_initializers = [
        qkv_weights_tensor,
        qkv_scales_tensor,
        qkv_zp_tensor,
    ]

    if has_bias:
        qkv_inputs.append("")  # empty g_idx
        qkv_bias_tensor, bias_tvi = concatenate_initializers(
            q_matmul, k_matmul, v_matmul, 5, extractor
        )
        new_tvis.append(bias_tvi)
        qkv_inputs.append(qkv_bias_tensor.name)
        new_initializers.append(qkv_bias_tensor)

    qkv_output_name = q_matmul.output[0].replace("q_proj", "qkv_proj")

    qkv_matmul = onnx.helper.make_node(
        "MatMulNBits",
        inputs=qkv_inputs,
        outputs=[qkv_output_name],
        domain=q_matmul.domain,
        name=f"MatMulNBits_{pass_id}",
    )

    with contextlib.suppress(ValueError):
        qkv_matmul.attribute.append(
            get_qkv_attribute((q_matmul, k_matmul, v_matmul), "accuracy_level", True)
        )
    qkv_matmul.attribute.append(
        get_qkv_attribute((q_matmul, k_matmul, v_matmul), "bits", True)
    )
    qkv_matmul.attribute.append(
        get_qkv_attribute((q_matmul, k_matmul, v_matmul), "block_size", True)
    )
    qkv_matmul.attribute.append(
        get_qkv_attribute((q_matmul, k_matmul, v_matmul), "K", True)
    )
    qkv_matmul.attribute.append(
        get_qkv_attribute((q_matmul, k_matmul, v_matmul), "N", False)
    )
    new_nodes.append(qkv_matmul)

    output_shape = list(
        ryzenai_onnx_utils.matcher.get_shape(q_matmul.output[0], extractor)
    )
    output_shape[-1] = onnx.helper.get_node_attr_value(qkv_matmul, "N")
    output_tvi = onnx.helper.make_tensor_value_info(
        qkv_output_name,
        ryzenai_onnx_utils.matcher.get_dtype(q_matmul.output[0], extractor),
        output_shape,
    )
    new_tvis.append(output_tvi)

    new_inputs = [
        qkv_output_name,
        # skipping empty key and value inputs
        "",
        "",
        *gqa.input[3:7],
        *q_rotary.input[2:4],
    ]

    new_node = onnx.helper.make_node(
        "GroupQueryAttention",
        inputs=new_inputs,
        outputs=gqa.output,
        name=gqa.name,
        domain=gqa.domain,
    )
    ryzenai_onnx_utils.matcher.copy_attributes(gqa, new_node)
    ryzenai_onnx_utils.matcher.set_attribute(new_node, "do_rotary", 1)
    with contextlib.suppress(ValueError):
        rotary_embedding_dim = onnx.helper.get_node_attr_value(
            q_rotary, "rotary_embedding_dim"
        )
        ryzenai_onnx_utils.matcher.add_attribute(
            new_node, "rotary_embedding_dim", rotary_embedding_dim
        )
    new_nodes.append(new_node)

    return new_nodes, new_initializers, new_tvis


PATTERN = [
    "MatMulNBits([?,?,?,?,?], [a0])",  # q
    "MatMulNBits([?,?,?,?,?], [a1])",  # k
    "MatMulNBits([?,?,?,?,?], [a2])",  # v
    "RotaryEmbedding([a0,?,?,?], a3)",
    "RotaryEmbedding([a1,?,?,?], a4)",
    "GroupQueryAttention([a3,a4,a2,?,?,?,?,?,?], [?,?,?])",
]
REPLACEMENT = replacement
