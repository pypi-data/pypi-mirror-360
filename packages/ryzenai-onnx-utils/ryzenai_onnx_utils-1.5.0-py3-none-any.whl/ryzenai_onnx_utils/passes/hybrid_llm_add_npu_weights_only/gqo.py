# Copyright (c) 2025 Advanced Micro Devices, Inc.

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

    k = onnx.helper.get_node_attr_value(node, "o_proj_K")
    n = onnx.helper.get_node_attr_value(node, "o_proj_N")
    block_size = onnx.helper.get_node_attr_value(node, "o_proj_block_size")
    assert len(node.input) == 10  # assuming no bias
    bias_offset = None
    if "is_bfp16" in params.attributes:
        ryzenai_onnx_utils.matcher.add_attribute(
            node, "is_bfp16", params.attributes["is_bfp16"]
        )
    packed_weight_tensor = (
        ryzenai_onnx_utils.transform.hybrid_llm.preprocess_matmulnbits_packed_weights(
            node, 7, extractor, k, n, block_size, bias_offset
        )
    )

    new_inputs = list(node.input[:7])
    new_initializers = [packed_weight_tensor]
    for i in range(7, 10):
        dtype = ryzenai_onnx_utils.matcher.get_dtype(node.input[i], extractor)
        new_name = node.input[i] + ".empty"
        new_initializers.append(onnx.helper.make_tensor(new_name, dtype, [0], []))
        new_inputs.append(new_name)

    new_inputs.append(packed_weight_tensor.name)
    new_node = onnx.helper.make_node(
        "GQO",
        inputs=new_inputs,
        outputs=node.output,
        domain=domain,
        name=node.name,
    )
    ryzenai_onnx_utils.matcher.copy_attributes(node, new_node)

    return (
        [new_node],
        new_initializers,
        None,
    )


REPLACEMENT = replacement
PATTERN = ["GQO([?,?,?,?,?,?,?,?], [?,?,?])"]
