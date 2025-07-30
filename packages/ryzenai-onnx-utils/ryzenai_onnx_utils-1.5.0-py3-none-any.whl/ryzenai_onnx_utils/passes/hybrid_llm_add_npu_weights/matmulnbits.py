# Copyright (c) 2024 Advanced Micro Devices, Inc.

import onnx

import ryzenai_onnx_utils.matcher
import ryzenai_onnx_utils.transform.hybrid_llm


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    node = subgraph[0]
    domain = params.get_domain(node.op_type)

    assert len(node.input) == 5

    k = onnx.helper.get_node_attr_value(node, "K")
    n = onnx.helper.get_node_attr_value(node, "N")
    block_size = onnx.helper.get_node_attr_value(node, "block_size")
    bias_offset = 3

    if "is_bfp16" in params.attributes:
        ryzenai_onnx_utils.matcher.add_attribute(
            node, "is_bfp16", params.attributes["is_bfp16"]
        )
    packed_weight_tensor = (
        ryzenai_onnx_utils.transform.hybrid_llm.preprocess_matmulnbits_packed_weights(
            node, 1, extractor, k, n, block_size, bias_offset
        )
    )
    new_inputs = [*node.input, packed_weight_tensor.name]
    new_initializers = [packed_weight_tensor]
    matmul_node = onnx.helper.make_node(
        node.op_type,
        inputs=new_inputs,
        outputs=node.output,
        domain=domain,
        name=node.name,
    )
    ryzenai_onnx_utils.matcher.copy_attributes(node, matmul_node)

    return [matmul_node], new_initializers, None


REPLACEMENT = [replacement] * 2
PATTERN = [["MatMulNBits([?,?,?,?,?], ?)"], ["MladfMatMul([?,?,?,?,?], ?)"]]
