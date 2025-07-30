# Copyright (c) 2024 Advanced Micro Devices, Inc.

import onnx


def add_reshape(input_name, shape_name, output_name, dtype, in_shape, out_shape):
    input_tvi = onnx.helper.make_tensor_value_info(input_name, dtype, in_shape)
    output_tvi = onnx.helper.make_tensor_value_info(output_name, dtype, out_shape)
    shape_tvi = onnx.helper.make_tensor_value_info(
        shape_name, onnx.TensorProto.INT64, [len(out_shape)]
    )
    # if there is only one dynamic dimension, set it to -1
    if sum(isinstance(o, str) for o in out_shape) == 1:
        numeric_out_shape = [-1 if isinstance(o, str) else o for o in out_shape]
    # if there is no dynamic dimension, set it to the original shape
    elif sum(isinstance(o, str) for o in out_shape) == 0:
        numeric_out_shape = list(out_shape)
    else:
        # zero dynamic dimension is not supported for now
        raise ValueError(
            f"Invalid output shape: {out_shape}, only one dynamic dimension is allowed"
        )

    node = onnx.helper.make_node(
        "Reshape",
        inputs=[input_name, shape_name],
        outputs=[output_name],
    )

    shape_tensor = onnx.helper.make_tensor(
        shape_name, onnx.TensorProto.INT64, [len(out_shape)], numeric_out_shape
    )

    return node, [input_tvi, output_tvi, shape_tvi], shape_tensor
