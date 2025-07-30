# Copyright (c) 2024 Advanced Micro Devices, Inc.

"""
This pass simplifies MatMulNBits operators that are in the original domain by
removing any optional inputs that are empty or zero.
"""

import onnx

import ryzenai_onnx_utils.matcher


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    matmul = subgraph[0]

    # if the matmul is not in its original domain, we cannot simplify anything
    if matmul.domain != "com.microsoft":
        return subgraph, [], None

    input_num = len(matmul.input)
    assert input_num <= 6, f"MatMulNBits {matmul.name} has more than 6 inputs"

    # this is already the simplest MatMulNBits
    if input_num == 3:
        return subgraph, [], None

    new_inputs = matmul.input[:3]
    bias_name = ""
    if input_num == 6:
        bias = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
            matmul.input[5], extractor
        )
        bias_name = matmul.input[5] if bias.any() else ""

    g_idx_name = matmul.input[4] if input_num >= 5 else ""

    zeros_name = ""
    if input_num >= 4 and matmul.input[3]:
        zeros = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
            matmul.input[3], extractor
        )
        zeros_name = matmul.input[3] if zeros.any() else ""

    if bias_name:
        new_inputs.extend([zeros_name, g_idx_name, bias_name])
    elif g_idx_name:
        new_inputs.extend([zeros_name, g_idx_name])
    elif zeros_name:
        new_inputs.append(zeros_name)

    new_node = onnx.helper.make_node(
        "MatMulNBits",
        inputs=new_inputs,
        outputs=matmul.output,
        name=matmul.name,
        domain=matmul.domain,
    )
    ryzenai_onnx_utils.matcher.copy_attributes(matmul, new_node)

    return [new_node], [], None


PATTERN = ["MatMulNBits([?,?,?,?,?,?], ?)"]
REPLACEMENT = replacement
