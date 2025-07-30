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
    cast_1 = subgraph[1]

    multiple_successors = ryzenai_onnx_utils.matcher.has_multiple_successors(
        cast_0.output[0], extractor.graph
    )
    assert not multiple_successors

    input_0 = ryzenai_onnx_utils.matcher.get_dtype(cast_0.input[0], extractor)
    output_0 = ryzenai_onnx_utils.matcher.get_dtype(cast_0.output[0], extractor)
    input_1 = ryzenai_onnx_utils.matcher.get_dtype(cast_1.input[0], extractor)
    output_1 = ryzenai_onnx_utils.matcher.get_dtype(cast_1.output[0], extractor)

    if input_0 == output_1 and output_0 == input_1:
        # rewrite the inputs and outputs of the adjacent nodes so they're directly
        # connected as if the cast never existed. This is necessary to preserve
        # the float16 type in the intermediate nodes of the model. Otherwise,
        # they get replaced by bfloat16 types
        prev_nodes = ryzenai_onnx_utils.matcher.find_nodes_by_output(
            cast_0.input[0], extractor.graph
        )
        assert len(prev_nodes) == 1
        prev_node = prev_nodes[0]
        for index, output_name in enumerate(prev_node.output):
            if output_name == cast_0.input[0]:
                prev_node.output[index] = cast_0.output[0]

        next_nodes = ryzenai_onnx_utils.matcher.find_nodes_by_input(
            cast_1.output[0], extractor.graph
        )
        for next_node in next_nodes:
            for index, input_name in enumerate(next_node.input):
                if input_name == cast_1.output[0]:
                    next_node.input[index] = cast_1.input[0]
        # return None to not do input/output rewriting since we do it manually
        return None, [], None
    return subgraph, [], None


PATTERN = [["Cast(?, a0)", "Cast(a0, ?)"], ["CastAvx(?, a0)", "CastAvx(a0, ?)"]]
REPLACEMENT = [replacement] * 2
