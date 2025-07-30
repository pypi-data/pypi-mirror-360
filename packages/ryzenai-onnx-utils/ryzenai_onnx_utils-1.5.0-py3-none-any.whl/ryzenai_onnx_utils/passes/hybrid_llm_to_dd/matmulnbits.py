# Copyright (c) 2025 Advanced Micro Devices, Inc.

import onnx

import ryzenai_onnx_utils.matcher
import ryzenai_onnx_utils.transform.hybrid_llm
import ryzenai_onnx_utils.utils
from ryzenai_onnx_utils.matcher import add_attribute
from ryzenai_onnx_utils.transform.cast import (
    add_cast_bfloat16_to_dtype,
    add_cast_dtype_to_bfloat16,
)


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    domain = params.get_domain("MladfMatMul")
    (matmul,) = subgraph

    assert len(matmul.input) == 6
    assert len(matmul.output) == 1

    tvis = []

    pre_cast_output = matmul.input[0] + f".out{pass_id}"
    matmul_input_shape = ryzenai_onnx_utils.matcher.get_shape(
        matmul.input[0], extractor
    )
    matmul_output_shape = ryzenai_onnx_utils.matcher.get_shape(
        matmul.output[0], extractor
    )
    pre_cast, pre_cast_tvi = add_cast_dtype_to_bfloat16(
        matmul.input[0],
        pre_cast_output,
        matmul_input_shape,
        domain,
        ryzenai_onnx_utils.matcher.get_dtype(matmul.input[0], extractor),
    )
    tvis.extend(pre_cast_tvi)

    new_inputs = [pre_cast_output]

    k = onnx.helper.get_node_attr_value(matmul, "K")
    n = onnx.helper.get_node_attr_value(matmul, "N")
    bias_offset = 4
    block_size = onnx.helper.get_node_attr_value(matmul, "block_size")
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

    matmul_output = matmul.output[0] + f".out{pass_id}"
    op_type = "MladfMatMul"
    matmul_node = onnx.helper.make_node(
        op_type,
        inputs=new_inputs,
        outputs=[matmul_output],
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

    post_cast, post_cast_tvi = add_cast_bfloat16_to_dtype(
        matmul.output[0] + f".out{pass_id}",
        matmul.output[0],
        matmul_output_shape,
        domain,
        ryzenai_onnx_utils.matcher.get_dtype(matmul.output[0], extractor),
    )
    tvis.extend(post_cast_tvi)

    return [*pre_cast, matmul_node, *post_cast], new_initializers, tvis


PATTERN = ["MatMulNBits([?,?,?,?], ?)"]
REPLACEMENT = replacement
