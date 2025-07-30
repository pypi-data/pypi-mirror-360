# Copyright (c) 2025 Advanced Micro Devices, Inc.

import onnx

import ryzenai_onnx_utils.matcher
import ryzenai_onnx_utils.transform.hybrid_llm
from ryzenai_onnx_utils.matcher import add_attribute
from ryzenai_onnx_utils.transform.cast import (
    add_cast_bfloat16_to_dtype_auto,
    add_cast_dtype_to_bfloat16_auto,
)


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    domain = params.get_domain("MladfMatMul")
    matmul = subgraph[0]
    pad = subgraph[2]

    assert len(matmul.input) == 6
    assert len(matmul.output) == 1

    new_nodes = []
    tvis = []

    matmul_output_shape = ryzenai_onnx_utils.matcher.get_shape(pad.output[0], extractor)
    pre_cast, pre_cast_tvi = add_cast_dtype_to_bfloat16_auto(
        matmul.input[0], pass_id, domain, extractor
    )
    new_nodes.extend(pre_cast)
    tvis.extend(pre_cast_tvi)

    keep_kv_dtype = False

    if keep_kv_dtype:
        post_cast, post_cast_tvi = add_cast_bfloat16_to_dtype_auto(
            pad.output[0], pass_id, domain, extractor
        )
        kv_output = post_cast[0].input[0]
        new_nodes.extend(post_cast)
        tvis.extend(post_cast_tvi)
    else:
        kv_output = pad.output[0]
        output_tvis = [
            onnx.helper.make_tensor_value_info(
                kv_output, onnx.TensorProto.BFLOAT16, matmul_output_shape
            )
        ]

        ryzenai_onnx_utils.matcher.remove_graph_outputs([kv_output], extractor.graph)

        extractor.graph.output.extend(output_tvis)
        tvis.extend(output_tvis)

    new_inputs = [pre_cast[0].output[0]]

    k = onnx.helper.get_node_attr_value(matmul, "K")
    n = onnx.helper.get_node_attr_value(matmul, "N")
    block_size = onnx.helper.get_node_attr_value(matmul, "block_size")
    bias_offset = 4
    if "is_bfp16" in params.attributes:
        ryzenai_onnx_utils.matcher.add_attribute(
            matmul, "is_bfp16", params.attributes["is_bfp16"]
        )
    new_weights, new_bias, new_scales, new_zeros = (
        ryzenai_onnx_utils.transform.hybrid_llm.preprocess_matmulnbits_weights(
            matmul, 1, extractor, k, n, block_size, bias_offset
        )
    )
    new_initializers = [new_weights, new_bias, new_scales, new_zeros]
    new_inputs.extend(
        (new_weights.name, new_bias.name, new_scales.name, new_zeros.name)
    )

    op_type = "MladfMatMul"
    matmul_node = onnx.helper.make_node(
        op_type,
        inputs=new_inputs,
        outputs=[kv_output],
        domain=domain,
        name=matmul.name,
    )
    ryzenai_onnx_utils.matcher.copy_attributes(matmul, matmul_node)
    add_attribute(matmul_node, "default_shape", 1)
    op_version = "v2" if "is_bfp16" in params.attributes else "flat"
    add_attribute(matmul_node, "op_version", op_version)
    add_attribute(
        matmul_node, "group_size", onnx.helper.get_node_attr_value(matmul, "block_size")
    )
    add_attribute(matmul_node, "total_seq_len", matmul_output_shape[2])
    new_nodes.append(matmul_node)

    return new_nodes, new_initializers, tvis


PATTERN = [
    "MatMulNBits([?,?,?,?], a0)",
    "Reshape([a0,?], a1)",
    "Pad([a1,?], ?)",
]
REPLACEMENT = replacement
