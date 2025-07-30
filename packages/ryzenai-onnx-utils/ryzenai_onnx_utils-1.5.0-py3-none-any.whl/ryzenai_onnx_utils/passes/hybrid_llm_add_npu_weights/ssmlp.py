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

    if node.op_type == "SSMLP":
        bias_enable = len(node.input) > 13
        bias_offset = 3
    else:
        bias_enable = len(node.input) > 15
        bias_offset = 4
    if bias_enable:
        matmuls = [
            (bias_offset, "gate"),
            (bias_offset + 4, "up"),
            (bias_offset + 8, "down"),
        ]
    else:
        matmuls = [
            (bias_offset, "gate"),
            (bias_offset + 3, "up"),
            (bias_offset + 6, "down"),
        ]

    if "is_bfp16" in params.attributes:
        ryzenai_onnx_utils.matcher.add_attribute(
            node, "is_bfp16", params.attributes["is_bfp16"]
        )

    new_initializers = []
    for index, label in matmuls:
        k = onnx.helper.get_node_attr_value(node, f"{label}_K")
        n = onnx.helper.get_node_attr_value(node, f"{label}_N")
        block_size = onnx.helper.get_node_attr_value(node, f"{label}_block_size")
        new_initializers.append(
            ryzenai_onnx_utils.transform.hybrid_llm.preprocess_matmulnbits_packed_weights(
                node, index, extractor, k, n, block_size, None
            )
        )
    new_names = [x.name for x in new_initializers]

    new_inputs = [*node.input, *new_names]
    new_node = onnx.helper.make_node(
        node.op_type,
        inputs=new_inputs,
        outputs=node.output,
        domain=domain,
        name=node.name,
    )
    ryzenai_onnx_utils.matcher.copy_attributes(node, new_node)

    return [new_node], new_initializers, None


REPLACEMENT = [replacement] * 2
PATTERN = [
    ["SSMLP([?,?,?,?,?,?,?,?,?,?,?,?,?], [?,?])"],
    ["SSGMLP([?,?,?,?,?,?,?,?,?,?,?,?,?,?,?], [?,?])"],
]
