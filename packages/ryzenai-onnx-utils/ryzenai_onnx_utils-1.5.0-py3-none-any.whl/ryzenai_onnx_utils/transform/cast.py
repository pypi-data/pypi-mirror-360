# Copyright (c) 2024 Advanced Micro Devices, Inc.

import math

import onnx

import ryzenai_onnx_utils.matcher

from .transpose import add_transpose


def _add_cast(input_name, output_name, shape, domain, operator, from_type, to_type):
    input_tvi = onnx.helper.make_tensor_value_info(input_name, from_type, shape)
    output_tvi = onnx.helper.make_tensor_value_info(output_name, to_type, shape)

    node = onnx.helper.make_node(
        operator,
        inputs=[input_name],
        outputs=[output_name],
        name=f"{input_name}_{output_name}",
        to=to_type,
        domain=domain,
    )
    return node, [input_tvi, output_tvi]


def float_to_bfloat16(input_name, output_name, shape, domain):
    return _add_cast(
        input_name,
        output_name,
        shape,
        domain,
        "CastAvx",
        onnx.TensorProto.FLOAT,
        onnx.TensorProto.BFLOAT16,
    )


def bfloat16_to_float(input_name, output_name, shape, domain):
    return _add_cast(
        input_name,
        output_name,
        shape,
        domain,
        "CastAvx",
        onnx.TensorProto.BFLOAT16,
        onnx.TensorProto.FLOAT,
    )


def float_to_float16(input_name, output_name, shape, domain):
    return _add_cast(
        input_name,
        output_name,
        shape,
        domain,
        "Cast",
        onnx.TensorProto.FLOAT,
        onnx.TensorProto.FLOAT16,
    )


def float16_to_float(input_name, output_name, shape, domain):
    return _add_cast(
        input_name,
        output_name,
        shape,
        domain,
        "Cast",
        onnx.TensorProto.FLOAT16,
        onnx.TensorProto.FLOAT,
    )


def float16_to_bfloat16(input_name, output_name, shape, domain):
    return _add_cast(
        input_name,
        output_name,
        shape,
        domain,
        "CastAvx",
        onnx.TensorProto.FLOAT16,
        onnx.TensorProto.BFLOAT16,
    )


def bfloat16_to_float16(input_name, output_name, shape, domain):
    return _add_cast(
        input_name,
        output_name,
        shape,
        domain,
        "CastAvx",
        onnx.TensorProto.BFLOAT16,
        onnx.TensorProto.FLOAT16,
    )


def add_cast_to_bf16(input_name, output_name, shape, domain):
    pre_cast, pre_cast_tvi = float_to_bfloat16(input_name, output_name, shape, domain)
    return [pre_cast], pre_cast_tvi


def add_cast_dtype_to_bfloat16(input_name, output_name, shape, domain, from_type):
    if from_type == onnx.TensorProto.FLOAT:
        pre_cast, pre_cast_tvi = float_to_bfloat16(
            input_name, output_name, shape, domain
        )
    elif from_type == onnx.TensorProto.FLOAT16:
        pre_cast, pre_cast_tvi = float16_to_bfloat16(
            input_name, output_name, shape, domain
        )
    else:
        pre_cast, pre_cast_tvi = _add_cast(
            input_name,
            output_name,
            shape,
            "",
            "Cast",
            from_type,
            onnx.TensorProto.BFLOAT16,
        )
    return [pre_cast], pre_cast_tvi


def add_cast_dtype_to_bfloat16_auto(
    name, pass_id, domain, extractor, shape=None, dtype=None
):
    if shape is None:
        shape = ryzenai_onnx_utils.matcher.get_shape(name, extractor)
    if dtype is None:
        dtype = ryzenai_onnx_utils.matcher.get_dtype(name, extractor)

    return add_cast_dtype_to_bfloat16(
        name, name + f".out{pass_id}", shape, domain, dtype
    )


def add_cast_bfloat16_to_dtype_auto(
    name, pass_id, domain, extractor, shape=None, dtype=None
):
    if shape is None:
        shape = ryzenai_onnx_utils.matcher.get_shape(name, extractor)
    if dtype is None:
        dtype = ryzenai_onnx_utils.matcher.get_dtype(name, extractor)
    return add_cast_bfloat16_to_dtype(
        name + f".out{pass_id}", name, shape, domain, dtype
    )


def add_cast_to_float(input_name, output_name, shape, domain):
    post_cast, post_cast_tvi = bfloat16_to_float(input_name, output_name, shape, domain)
    return [post_cast], post_cast_tvi


def add_cast_bfloat16_to_dtype(input_name, output_name, shape, domain, to_type):
    if to_type == onnx.TensorProto.FLOAT:
        post_cast, post_cast_tvi = bfloat16_to_float(
            input_name, output_name, shape, domain
        )
    elif to_type == onnx.TensorProto.FLOAT16:
        post_cast, post_cast_tvi = bfloat16_to_float16(
            input_name, output_name, shape, domain
        )
    else:
        post_cast, post_cast_tvi = _add_cast(
            input_name,
            output_name,
            shape,
            "",
            "Cast",
            onnx.TensorProto.BFLOAT16,
            to_type,
        )
    return [post_cast], post_cast_tvi


def add_redundant_casts(direction, input_name, output_name, via_type, extractor):
    name = input_name if direction == 0 else output_name
    shape = ryzenai_onnx_utils.matcher.get_shape(name, extractor)
    dtype = ryzenai_onnx_utils.matcher.get_dtype(name, extractor)

    new_nodes = []
    intermediate_net = input_name + ".inter"
    first_cast, new_tvis = _add_cast(
        input_name,
        intermediate_net,
        shape,
        "",
        "Cast",
        dtype,
        via_type,
    )
    new_nodes.append(first_cast)

    second_cast, second_cast_tvis = _add_cast(
        intermediate_net,
        output_name,
        shape,
        "",
        "Cast",
        via_type,
        dtype,
    )
    new_nodes.append(second_cast)
    new_tvis.extend(second_cast_tvis)
    return new_nodes, new_tvis


def add_redundant_input_casts(input_name, via_type, extractor):
    return add_redundant_casts(0, input_name, input_name + ".out", via_type, extractor)


def add_redundant_output_casts(output_name, via_type, extractor):
    return add_redundant_casts(1, output_name + ".in", output_name, via_type, extractor)


def add_cast_to_float_and_add_silu(
    input_name, output_name, shape, index, channels_last, domain
):
    silu_output = input_name + ".silu"
    input_tvi = onnx.helper.make_tensor_value_info(
        input_name, onnx.TensorProto.BFLOAT16, shape
    )
    output_tvi = onnx.helper.make_tensor_value_info(
        silu_output, onnx.TensorProto.BFLOAT16, shape
    )

    node = onnx.helper.make_node(
        "SILU_noqdq",
        inputs=[input_name],
        outputs=[silu_output],
        name=f"SILU_noqdq_{index}",
    )
    silu_tvi = [input_tvi, output_tvi]
    tvis = silu_tvi
    if channels_last == 0:
        n = shape[1]
        m = shape[2]
        k = shape[3]
        transpose_output_in = silu_output + f".out{index}"
        transpose_in, transpose_tvi_in = add_transpose(
            f"Transpose_{index}",
            silu_output,
            transpose_output_in,
            onnx.TensorProto.BFLOAT16,
            [1, m, k, n],
            [1, n, m, k],
            [0, 3, 1, 2],
        )
        post_cast, post_cast_tvi = bfloat16_to_float(
            transpose_output_in, output_name, shape, domain
        )
        tvis.extend(transpose_tvi_in)
        tvis.extend(post_cast_tvi)
        return [post_cast, node, transpose_in], tvis
    else:
        post_cast, post_cast_tvi = bfloat16_to_float(
            silu_output, output_name, shape, domain
        )
        tvis.extend(post_cast_tvi)
    return [post_cast, node], tvis


def add_cast_to_float_and_add_bfp_silu(
    input_name, output_name, shape, index, channels_last, domain
):
    silu_output = input_name + ".silu_bfp"
    input_tvi = onnx.helper.make_tensor_value_info(
        input_name, onnx.TensorProto.BFLOAT16, shape
    )
    bfp_out_size = int(math.prod(shape) / 8 * 9)
    output_tvi = onnx.helper.make_tensor_value_info(
        silu_output, onnx.TensorProto.UINT8, [1, bfp_out_size]
    )

    node = onnx.helper.make_node(
        "SILU_noqdq",
        inputs=[input_name],
        outputs=[silu_output],
        name=f"SILU_noqdq_{index}_bfp",
        bfp16_tensors=[silu_output],
        bfp16_shape_0=shape,
    )
    silu_tvi = [input_tvi, output_tvi]
    tvis = silu_tvi

    bfp_to_bf_input_tvi = onnx.helper.make_tensor_value_info(
        silu_output, onnx.TensorProto.UINT8, [1, bfp_out_size]
    )
    bfp_to_bf_output = silu_output + f".out{index}_silu_bfp_bf"
    bfp_to_bf_output_tvi = onnx.helper.make_tensor_value_info(
        bfp_to_bf_output, onnx.TensorProto.BFLOAT16, shape
    )
    bfp_to_bf_tvi_v = [bfp_to_bf_input_tvi, bfp_to_bf_output_tvi]
    tvis.extend(bfp_to_bf_tvi_v)

    # Dummy node which will be removed in scope of simplify_bfps
    bfp_to_bf_node = onnx.helper.make_node(
        "BFP16_to_BF16",
        inputs=[silu_output],
        outputs=[bfp_to_bf_output],
        domain=domain,
        name=f"bfp16_to_bf16_{index}_silu",
        bfp16_tensors=[silu_output],
        bfp16_shape_0=shape,
    )

    if channels_last == 0:
        n = shape[1]
        m = shape[2]
        k = shape[3]
        transpose_output_in = silu_output + f".out{index}_silu"
        transpose_in, transpose_tvi_in = add_transpose(
            f"Transpose_{index}_silu",
            bfp_to_bf_output,
            transpose_output_in,
            onnx.TensorProto.BFLOAT16,
            [1, m, k, n],
            [1, n, m, k],
            [0, 3, 1, 2],
        )
        post_cast, post_cast_tvi = bfloat16_to_float(
            transpose_output_in, output_name, shape, domain
        )
        tvis.extend(transpose_tvi_in)
        tvis.extend(post_cast_tvi)
        return [post_cast, node, bfp_to_bf_node, transpose_in], tvis
    else:
        post_cast, post_cast_tvi = bfloat16_to_float(
            bfp_to_bf_output, output_name, shape, domain
        )
        tvis.extend(post_cast_tvi)
    return [post_cast, node, bfp_to_bf_node], tvis
