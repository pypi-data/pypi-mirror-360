# Copyright (c) 2025 Advanced Micro Devices, Inc.

"""
This pass aims to reduce the computation and tensor memory allocation of the
last MatMulNBits node (lm_head) in LLMs by pruning the last output from seq_len
-> 1.
"""

import onnx

import ryzenai_onnx_utils.matcher
from ryzenai_onnx_utils.passes import global_pass


def is_logits_node(output_name: str):
    return "logits" in output_name


def pruned_tvi(name: str, extractor: onnx.utils.Extractor):
    dtype = ryzenai_onnx_utils.matcher.get_dtype(name, extractor)
    shape = ryzenai_onnx_utils.matcher.get_shape(name, extractor)
    new_shape = [shape[0], 1, shape[2]]

    new_tvi = onnx.helper.make_tensor_value_info(name, dtype, new_shape)

    return new_tvi


@global_pass
def prune_logits(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    # skip this pass if prune_logits is disabled
    prune_logits = params.get_bool_attr("prune_logits", False)
    if not prune_logits:
        return

    domain = params.get_domain("MatMulNBits")

    for index, output_tvi in enumerate(extractor.graph.output):
        parents = ryzenai_onnx_utils.matcher.find_nodes_by_output(
            output_tvi.name, extractor.graph
        )
        assert len(parents) == 1
        parent_node = parents[0]
        if not is_logits_node(output_tvi.name) or parent_node.domain != domain:
            continue

        new_tvi = pruned_tvi(output_tvi.name, extractor)

        extractor.graph.output.remove(extractor.graph.output[index])
        extractor.graph.output.insert(index, new_tvi)


PATTERN = []
REPLACEMENT = prune_logits
