# Copyright (c) 2024 Advanced Micro Devices, Inc.

import onnx


def add_transpose(
    node_name, input_name, output_name, dtype, shape_prev, shape_after, perm_vec
):
    input_tvi = onnx.helper.make_tensor_value_info(input_name, dtype, shape_prev)
    output_tvi = onnx.helper.make_tensor_value_info(output_name, dtype, shape_after)

    node = onnx.helper.make_node(
        "Transpose",
        inputs=[input_name],
        outputs=[output_name],
        name=node_name,
        perm=perm_vec,
    )

    return node, [input_tvi, output_tvi]
