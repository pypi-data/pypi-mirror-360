# Copyright (c) 2024 Advanced Micro Devices, Inc.


import onnx

import ryzenai_onnx_utils.matcher


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    node = subgraph[0]

    if node.domain != params.get_domain(node.op_type):
        return subgraph, [], None

    try:
        onnx.helper.get_node_attr_value(node, "hybrid_llm_cast_input")
    except ValueError:
        ryzenai_onnx_utils.matcher.add_attribute(
            node, "hybrid_llm_cast_input", [], onnx.AttributeProto.INTS
        )

    try:
        onnx.helper.get_node_attr_value(node, "hybrid_llm_cast_output")
    except ValueError:
        ryzenai_onnx_utils.matcher.add_attribute(
            node, "hybrid_llm_cast_output", [], onnx.AttributeProto.INTS
        )
    return [node], [], None


PATTERN = ["?(?, ?)"]
REPLACEMENT = replacement
