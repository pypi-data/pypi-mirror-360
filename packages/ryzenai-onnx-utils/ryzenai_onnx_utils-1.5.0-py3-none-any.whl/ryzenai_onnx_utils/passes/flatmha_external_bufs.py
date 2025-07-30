# Copyright (c) 2025 Advanced Micro Devices, Inc.

import onnx
import ryzenai_dynamic_dispatch.onnx_graph as og

import ryzenai_onnx_utils.utils


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    mul_func = int(og.StateOperation.MUL)
    mha = subgraph[-1]

    # TODO(varunsh): this is assuming the pass_id will be separated by underscores
    # get the count of how many passes have run and use that to offset the indices below
    # this is also assuming the order of the subpasses below
    subpass_index = int(pass_id.split("_")[1])
    match_index = int(pass_id.split("_")[2])
    buffer_offset = (subpass_index + match_index) * 4
    alias_offset = (subpass_index + match_index) * 2

    if ryzenai_onnx_utils.matcher.has_attribute(mha, "external_buffers"):
        return subgraph, [], None

    external_buffers = []
    # first is the onnx arg index (inputs + outputs) and second is buffer index,
    # third is index in the buffer, fourth is an alias index
    external_buffers.extend([4, 0, 0, 0])  # sin/cos cache
    external_buffers.extend([1, 1, buffer_offset + 0, alias_offset + 0])  # past k
    external_buffers.extend([2, 1, buffer_offset + 1, alias_offset + 1])  # past v
    external_buffers.extend([6, 1, buffer_offset + 2, alias_offset + 0])  # present k
    ryzenai_onnx_utils.matcher.add_attribute(mha, "external_buffers", external_buffers)

    # [onnx_arg_index, state_table_idx, function, function_arg]
    # for LLMs, there's only one state table so set it to zero here

    # sin/cos
    sin_cos_shape = ryzenai_onnx_utils.matcher.get_shape(mha.input[4], extractor)
    ryzenai_onnx_utils.matcher.add_attribute(
        mha, "update_tensor_offsets", [4, 0, mul_func, sin_cos_shape[-1] * 2]
    )

    # present_k
    present_k_shape = ryzenai_onnx_utils.matcher.get_shape(mha.output[1], extractor)
    ryzenai_onnx_utils.matcher.append_value_in_attribute(
        mha, "update_tensor_offsets", [6, 0, mul_func, present_k_shape[-1] * 2]
    )

    if len(subgraph) > 1:
        matmul = subgraph[2]

        external_buffers = []
        # present v
        external_buffers.extend([5, 1, buffer_offset + 3, alias_offset + 1])
        ryzenai_onnx_utils.matcher.add_attribute(
            matmul, "external_buffers", external_buffers
        )

        present_v_shape = ryzenai_onnx_utils.matcher.get_shape(
            matmul.output[0], extractor
        )
        ryzenai_onnx_utils.matcher.add_attribute(
            matmul,
            "update_tensor_offsets",
            [5, 0, mul_func, present_v_shape[-1] * 2],
        )

    return subgraph, [], None


PATTERN = [
    [
        "CastAvx(?, a1)",
        "MladfMatMul([a1,?,?,?,?], a0)",
        "MladfMatMul([a1,?,?,?,?], ?)",
        "FLATMHA([a0,?,?,?,?], [?,?])",
    ],
    [
        "FlatRMSAdd([?,?], [?, a1])",
        "MladfMatMul([a1,?,?,?,?], a0)",
        "MladfMatMul([a1,?,?,?,?], ?)",
        "FLATMHA([a0,?,?,?,?], [?,?])",
    ],
    [
        "SkipSimplifiedLayerNormalization([?,?,?], [a1,?,?,?])",
        "MladfMatMul([a1,?,?,?,?], a0)",
        "MladfMatMul([a1,?,?,?,?], ?)",
        "FLATMHA([a0,?,?,?,?], [?,?])",
    ],
]
REPLACEMENT = [replacement] * 3
