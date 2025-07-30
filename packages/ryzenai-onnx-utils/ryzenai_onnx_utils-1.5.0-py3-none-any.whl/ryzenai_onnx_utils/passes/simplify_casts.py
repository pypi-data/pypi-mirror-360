# Copyright (c) 2024 Advanced Micro Devices, Inc.


import onnx

import ryzenai_onnx_utils.matcher


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    cast_0 = subgraph[0]
    input_0 = ryzenai_onnx_utils.matcher.get_dtype(cast_0.input[0], extractor)
    output_0 = ryzenai_onnx_utils.matcher.get_dtype(cast_0.output[0], extractor)

    if len(subgraph) == 1:
        # this is a pointless cast - a cast casting from one type to the same type
        if input_0 == output_0:
            return [], [], None
        return subgraph, [], None

    cast_1 = subgraph[1]
    input_1 = ryzenai_onnx_utils.matcher.get_dtype(cast_1.input[0], extractor)
    output_1 = ryzenai_onnx_utils.matcher.get_dtype(cast_1.output[0], extractor)

    multiple_successors = ryzenai_onnx_utils.matcher.has_multiple_successors(
        cast_0.output[0], extractor.graph
    )

    if input_0 == output_1 and output_0 == input_1:
        if not multiple_successors:
            return [], [], None
        # in this case, we need to keep the first cast around because its output
        # is going to multiple places but there is also a second redundant cast
        # to some nodes. Find the nodes where this second cast output is going
        # and rewrite it to the first cast's input
        cast_1_successors = ryzenai_onnx_utils.matcher.find_nodes_by_input(
            cast_1.output[0], extractor.graph
        )
        for node in cast_1_successors:
            for index, input_name in enumerate(node.input):
                if input_name == cast_1.output[0]:
                    node.input[index] = cast_0.input[0]
        return [cast_0], [], None
    return subgraph, [], None


PATTERN = [
    ["CastAvx(?, a0)", "CastAvx(a0, ?)"],
    ["Cast(?, a0)", "Cast(a0, ?)"],
    ["CastAvx(?, ?)"],
    ["Cast(?, ?)"],
]
REPLACEMENT = [replacement] * len(PATTERN)
