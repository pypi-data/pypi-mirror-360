# Copyright (c) 2025 Advanced Micro Devices, Inc.

import contextlib

import ml_dtypes
import numpy as np
import onnx

import ryzenai_onnx_utils.matcher
import ryzenai_onnx_utils.transform
import ryzenai_onnx_utils.transform.reshape
from ryzenai_onnx_utils.transform.cast import (
    add_cast_bfloat16_to_dtype_auto,
    add_cast_dtype_to_bfloat16_auto,
)


def concatenate_initializers(q_matmul, k_matmul, index, extractor):
    q_np = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
        q_matmul.input[index], extractor
    )
    k_np = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
        k_matmul.input[index], extractor
    )

    qk_np = np.concatenate((q_np, k_np), 0)
    qk_np_name: str = q_matmul.input[index].replace("q_proj", "qk_proj")
    qk_np_name = qk_np_name.replace("Add", "MatMulNBits")
    qk_tensor = onnx.numpy_helper.from_array(qk_np, qk_np_name)
    tvi = onnx.helper.make_tensor_value_info(
        qk_np_name, onnx.helper.np_dtype_to_tensor_dtype(qk_np.dtype), qk_np.shape
    )
    return qk_tensor, tvi


def get_qk_attribute(matmuls, attr_name, check_equal):
    """
    Go through the qk matmuls and extract the attribute values. Check if they're
    equal, except for the case of N where we add them together

    Args:
        matmuls (list[NodeProto]): q, k matmuls
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


def replace_output_shape(graph: onnx.GraphProto, output_name, dtype, new_shape):
    index = next(i for i, v in enumerate(graph.output) if v.name == output_name)
    graph.output.pop(index)
    new_tvi = onnx.helper.make_tensor_value_info(output_name, dtype, new_shape)
    graph.output.insert(index, new_tvi)


def create_sin_cos_cache(extractor):
    sin_cache = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
        "sin_cache", extractor
    )
    cos_cache = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
        "cos_cache", extractor
    )
    sin_cos_cache = np.concatenate((cos_cache, sin_cache), 1)

    if sin_cos_cache.dtype != ml_dtypes.bfloat16:
        sin_cos_cache = sin_cos_cache.astype(ml_dtypes.bfloat16)
    sin_cos_cache_tensor = onnx.helper.make_tensor(
        "sin_cos_cache",
        onnx.TensorProto.BFLOAT16,
        sin_cos_cache.shape,
        sin_cos_cache.tobytes(),
        True,
    )

    sin_cos_cache_node = onnx.helper.make_node(
        "Constant",
        inputs=[],
        outputs=["sin_cos_cache_val"],
        value=sin_cos_cache_tensor,
        name="sin_cos_cache",
    )
    new_tvi = onnx.helper.make_tensor_value_info(
        "sin_cos_cache_val",
        onnx.TensorProto.BFLOAT16,
        sin_cos_cache.shape,
    )
    return sin_cos_cache_node, new_tvi


def add_attention_mask():
    new_nodes = []
    new_tvis = []

    attn_mask_node = onnx.helper.make_node(
        "Constant",
        inputs=[],
        outputs=["attention_mask_const"],
        value_ints=[1],
        name="attn_mask_node",
    )
    new_nodes.append(attn_mask_node)
    new_tvis.append(
        onnx.helper.make_tensor_value_info(
            "attention_mask_const",
            onnx.TensorProto.INT64,
            [1],
        )
    )

    cast_node = onnx.helper.make_node(
        "Cast",
        # before sub
        inputs=["/model/attn_mask_reformat/attn_mask_subgraph/ReduceSum/output_0"],
        # after sub
        # inputs=["/model/attn_mask_reformat/attn_mask_subgraph/Sub/output_0"],
        outputs=["attention_mask_casted"],
        name="attn_cast",
        to=onnx.TensorProto.UINT32,
    )
    new_nodes.append(cast_node)
    new_tvis.append(
        onnx.helper.make_tensor_value_info(
            "attention_mask_casted",
            onnx.TensorProto.UINT32,
            [1, 1],
        )
    )

    reshape_node = onnx.helper.make_node(
        "Reshape",
        name="attn_mask_reshape",
        inputs=["attention_mask_casted", "attention_mask_const"],
        outputs=["attention_mask_const_uint"],
    )
    new_tvis.append(
        onnx.helper.make_tensor_value_info(
            "attention_mask_const_uint",
            onnx.TensorProto.UINT32,
            [1],
        )
    )
    new_nodes.append(reshape_node)

    return new_nodes, new_tvis


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    domain = params.get_domain("FLATMHA")
    q_matmul = subgraph[0]
    k_matmul = subgraph[1]
    v_matmul = subgraph[2]
    # q_rotary = subgraph[3]
    # k_rotary = subgraph[4]
    gqa = subgraph[5]

    # assuming matmulnbits have weights, scales, zero points, g_idx, and bias
    assert len(q_matmul.input) == len(k_matmul.input) == len(v_matmul.input)
    assert len(q_matmul.input) == 6, len(q_matmul.input)
    assert q_matmul.input[0] == k_matmul.input[0] == v_matmul.input[0]

    qk_weights_tensor, weights_tvi = concatenate_initializers(
        q_matmul, k_matmul, 1, extractor
    )
    qk_scales_tensor, scales_tvi = concatenate_initializers(
        q_matmul, k_matmul, 2, extractor
    )
    qk_zp_tensor, zp_tvi = concatenate_initializers(q_matmul, k_matmul, 3, extractor)

    qk_bias_tensor, bias_tvi = concatenate_initializers(
        q_matmul, k_matmul, 5, extractor
    )

    new_tvis = [weights_tvi, scales_tvi, zp_tvi, bias_tvi]
    qk_inputs = [
        q_matmul.input[0],
        qk_weights_tensor.name,
        qk_scales_tensor.name,
        qk_zp_tensor.name,
        "",  # assuming g_idx is not used
        qk_bias_tensor.name,
    ]
    new_initializers = [
        qk_weights_tensor,
        qk_scales_tensor,
        qk_zp_tensor,
        qk_bias_tensor,
    ]

    qk_output_name = q_matmul.output[0].replace("q_proj", "qk_proj")

    qk_matmul = onnx.helper.make_node(
        "MatMulNBits",
        inputs=qk_inputs,
        outputs=[qk_output_name],
        domain=q_matmul.domain,
        name=f"MatMulNBits_{pass_id}",
    )

    with contextlib.suppress(ValueError):
        qk_matmul.attribute.append(
            get_qk_attribute((q_matmul, k_matmul), "accuracy_level", True)
        )
    qk_matmul.attribute.append(get_qk_attribute((q_matmul, k_matmul), "bits", True))
    qk_matmul.attribute.append(
        get_qk_attribute((q_matmul, k_matmul), "block_size", True)
    )
    qk_matmul.attribute.append(get_qk_attribute((q_matmul, k_matmul), "K", True))
    qk_matmul.attribute.append(get_qk_attribute((q_matmul, k_matmul), "N", False))

    new_nodes = [qk_matmul]

    output_shape = list(
        ryzenai_onnx_utils.matcher.get_shape(q_matmul.output[0], extractor)
    )
    output_shape[-1] = onnx.helper.get_node_attr_value(qk_matmul, "N")
    output_dtype = ryzenai_onnx_utils.matcher.get_dtype(q_matmul.output[0], extractor)
    output_tvi = onnx.helper.make_tensor_value_info(
        qk_output_name,
        output_dtype,
        output_shape,
    )
    new_tvis.append(output_tvi)

    new_nodes.append(v_matmul)

    v_matmul_shape = ryzenai_onnx_utils.matcher.get_shape(v_matmul.output[0], extractor)
    past_k_shape = ryzenai_onnx_utils.matcher.get_shape(gqa.input[3], extractor)
    past_v_shape = ryzenai_onnx_utils.matcher.get_shape(gqa.input[4], extractor)

    replace_output_shape(
        extractor.graph,
        gqa.output[1],
        ryzenai_onnx_utils.matcher.get_dtype(gqa.output[1], extractor),
        past_k_shape,
    )
    replace_output_shape(
        extractor.graph,
        gqa.output[2],
        ryzenai_onnx_utils.matcher.get_dtype(gqa.output[2], extractor),
        past_v_shape,
    )

    present_v_shape = ryzenai_onnx_utils.matcher.get_shape(gqa.output[2], extractor)
    assert present_v_shape[0] == v_matmul_shape[0]
    assert present_v_shape[1] * present_v_shape[3] == v_matmul_shape[2]
    reshaped_shape = [present_v_shape[0], present_v_shape[1], 1, present_v_shape[3]]
    reshaped_output = v_matmul.output[0] + ".reshaped"
    v_matmul_dtype = ryzenai_onnx_utils.matcher.get_dtype(v_matmul.output[0], extractor)
    reshape, reshape_tvis, reshape_tensors = (
        ryzenai_onnx_utils.transform.reshape.add_reshape(
            v_matmul.output[0],
            "present_v_reshape",
            reshaped_output,
            v_matmul_dtype,
            v_matmul_shape,
            reshaped_shape,
        )
    )
    new_nodes.append(reshape)
    new_tvis.extend(reshape_tvis)
    new_initializers.append(reshape_tensors)

    pad_tensor = onnx.helper.make_tensor(
        "pad_tensor",
        onnx.TensorProto.INT64,
        [8],
        [0, 0, 0, 0, 0, 0, present_v_shape[2] - 1, 0],
    )
    new_initializers.append(pad_tensor)
    pad = onnx.helper.make_node(
        "Pad",
        inputs=[reshaped_output, "pad_tensor"],
        outputs=[gqa.output[2]],
        name=v_matmul.name + ".pad",
    )
    new_nodes.append(pad)

    pre_cast_qk, pre_cast_qk_tvi = add_cast_dtype_to_bfloat16_auto(
        qk_output_name, pass_id, domain, extractor, output_shape, output_dtype
    )
    new_nodes.extend(pre_cast_qk)
    new_tvis.extend(pre_cast_qk_tvi)

    keep_kv_dtype = False

    if keep_kv_dtype:
        pre_cast_past_k, pre_cast_past_k_tvi = add_cast_dtype_to_bfloat16_auto(
            gqa.input[3], pass_id, domain, extractor
        )
        new_nodes.extend(pre_cast_past_k)
        new_tvis.extend(pre_cast_past_k_tvi)

        pre_cast_past_v, pre_cast_past_v_tvi = add_cast_dtype_to_bfloat16_auto(
            gqa.input[4], pass_id, domain, extractor
        )
        new_nodes.extend(pre_cast_past_v)
        new_tvis.extend(pre_cast_past_v_tvi)

        kv_inputs = [pre_cast_past_k[0].output[0], pre_cast_past_v[0].output[0]]
    else:
        kv_inputs = [gqa.input[3], gqa.input[4]]

        input_tvis = []
        for kv_name in kv_inputs:
            input_tvis.append(
                onnx.helper.make_tensor_value_info(
                    kv_name, onnx.TensorProto.BFLOAT16, past_k_shape
                )
            )

        ryzenai_onnx_utils.matcher.remove_graph_inputs(kv_inputs, extractor.graph)

        extractor.graph.input.extend(input_tvis)
        new_tvis.extend(input_tvis)

    # use a common tensor across the whole model
    sin_cos_exists = ryzenai_onnx_utils.matcher.find_consts(
        "sin_cos_cache_val", extractor.graph
    )
    if not sin_cos_exists:
        sin_cos_cache, sin_cos_cache_tvi = create_sin_cos_cache(extractor)
        new_nodes.append(sin_cos_cache)
        new_tvis.append(sin_cos_cache_tvi)

    attention_mask_exists = ryzenai_onnx_utils.matcher.find_nodes_by_output(
        "attention_mask_const_uint", extractor.graph
    )
    if not attention_mask_exists:
        attn_mask_nodes, attn_mask_tvis = add_attention_mask()
        new_nodes.extend(attn_mask_nodes)
        new_tvis.extend(attn_mask_tvis)

    new_inputs = [
        pre_cast_qk[0].output[0],
        # past key and value
        *kv_inputs,
        # attn mask - this should be discovered by tracing back gqa.input[5] to the model input
        "attention_mask_const_uint",
        # sin cos cache
        "sin_cos_cache_val",
    ]

    post_cast_output, post_cast_output_tvi = add_cast_bfloat16_to_dtype_auto(
        gqa.output[0], pass_id, domain, extractor
    )
    new_nodes.extend(post_cast_output)
    new_tvis.extend(post_cast_output_tvi)

    if keep_kv_dtype:
        post_cast_present_k, post_cast_present_k_tvi = add_cast_bfloat16_to_dtype_auto(
            gqa.output[1], pass_id, domain, extractor
        )
        new_nodes.extend(post_cast_present_k)
        new_tvis.extend(post_cast_present_k_tvi)

        kv_output = post_cast_present_k[0].input[0]
    else:
        kv_output = gqa.output[1]
        output_tvis = [
            onnx.helper.make_tensor_value_info(
                kv_output, onnx.TensorProto.BFLOAT16, past_k_shape
            )
        ]

        ryzenai_onnx_utils.matcher.remove_graph_outputs([kv_output], extractor.graph)

        extractor.graph.output.extend(output_tvis)
        new_tvis.extend(output_tvis)

    new_outputs = [post_cast_output[0].input[0], kv_output]

    new_node = onnx.helper.make_node(
        "FLATMHA",
        inputs=new_inputs,
        outputs=new_outputs,
        name=gqa.name,
        domain=domain,
    )
    ryzenai_onnx_utils.matcher.copy_attributes(gqa, new_node)

    kv_num_heads = past_k_shape[1]
    num_heads = onnx.helper.get_node_attr_value(gqa, "num_heads")
    seq_len = output_shape[1]
    total_seq_len = past_k_shape[2]
    head_size = past_k_shape[3]
    ryzenai_onnx_utils.matcher.add_attribute(
        new_node,
        "input_shape",
        [kv_num_heads, num_heads, seq_len, total_seq_len, head_size],
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
