# Copyright (c) 2024 Advanced Micro Devices, Inc.


import onnx

import ryzenai_onnx_utils.matcher
from ryzenai_onnx_utils.passes import SubPass


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    cast = subgraph[0]
    to_type = onnx.helper.get_node_attr_value(cast, "to")

    # if the cast has already been pruned, it will have no nodes that take its
    # output as input
    output_nodes = ryzenai_onnx_utils.matcher.find_nodes_by_input(
        cast.output[0], extractor.graph
    )
    if (not output_nodes) and (
        not ryzenai_onnx_utils.matcher.is_output_edge(cast.output[0], extractor.graph)
    ):
        # return None for subgraph to not do any input/output rewriting in the matcher
        return None, [], None

    # all nodes that have the same input as this cast
    sibling_nodes = ryzenai_onnx_utils.matcher.find_nodes_by_input(
        cast.input[0], extractor.graph
    )

    for sibling in sibling_nodes:
        if sibling.op_type != cast.op_type:
            continue
        if sibling.name == cast.name:
            continue
        if onnx.helper.get_node_attr_value(sibling, "to") != to_type:
            continue
        # import pdb; pdb.set_trace()
        # all nodes that have the same input as the output of this sibling cast
        sibling_dsts = ryzenai_onnx_utils.matcher.find_nodes_by_input(
            sibling.output[0], extractor.graph
        )
        for sibling_dst in sibling_dsts:
            for index, io in enumerate(sibling_dst.input):
                if io == sibling.output[0]:
                    sibling_dst.input[index] = cast.output[0]

    return subgraph, [], None


PATTERN = [SubPass("CastAvx", ["CastAvx(?, ?)"]), SubPass("Cast", ["Cast(?, ?)"])]
REPLACEMENT = replacement
