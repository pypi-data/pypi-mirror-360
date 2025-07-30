# Copyright (c) 2025 Advanced Micro Devices, Inc.

import onnx

import ryzenai_onnx_utils.matcher
from ryzenai_onnx_utils.passes import global_pass


@global_pass
def remove_unused_inputs(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    inputs_to_remove = []
    for index, input_tvi in enumerate(extractor.model.graph.input):
        if not ryzenai_onnx_utils.matcher.is_used_input(
            input_tvi.name, extractor.model.graph
        ):
            inputs_to_remove.append(index)
    sorted_indices = sorted(inputs_to_remove, reverse=True)
    for index in sorted_indices:
        del extractor.model.graph.input[index]


PATTERN = []
REPLACEMENT = remove_unused_inputs
