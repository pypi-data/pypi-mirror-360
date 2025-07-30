# Copyright (c) 2024 Advanced Micro Devices, Inc.

import numpy as np
import onnx
from ryzenai_dynamic_dispatch import matmulnbits

import ryzenai_onnx_utils
import ryzenai_onnx_utils.utils


def _extract_arrays(
    node: onnx.NodeProto,
    start_index: int,
    extractor: onnx.utils.Extractor,
    n: int,
    bias_offset: int,
):
    weight = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
        node.input[start_index], extractor
    )
    scales = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
        node.input[start_index + 1], extractor
    )
    # TODO(varunsh): should detect if present and set asymmetric if so
    zero_point = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
        node.input[start_index + 2], extractor
    )

    if bias_offset is not None:
        bias = ryzenai_onnx_utils.matcher.get_initializer_as_numpy(
            node.input[start_index + bias_offset], extractor
        )
    else:
        bias = np.zeros((n, 1))

    # TODO(varunsh): update
    asymmetric_quant = True

    try:
        is_bfp16 = onnx.helper.get_node_attr_value(node, "is_bfp16").decode("utf-8")
    except ValueError:
        mladf_version = "v1"
    else:
        if is_bfp16 == "weights":
            mladf_version = "v2"
        elif not is_bfp16:
            mladf_version = "v1"
        else:
            raise ValueError(f"Unsupported is_bfp16: {is_bfp16}")

    return (weight, scales, zero_point, bias, asymmetric_quant, mladf_version)


def preprocess_matmulnbits_weights(
    node, start_index, extractor, k, n, block_size, bias_offset
):
    (weight, scales, zero_point, bias, asymmetric_quant, mladf_version) = (
        _extract_arrays(node, start_index, extractor, n, bias_offset)
    )
    bias_enable = bias_offset > 0

    if bias_enable:
        bias_name = node.input[start_index + bias_offset]
    else:
        bias_name = ryzenai_onnx_utils.matcher.input_name_from_node_name(
            node.name, "bias"
        )

    try:
        new_weight, new_bias, new_scales, new_zeros = matmulnbits.matmulnbits_preformat(
            weight.astype(np.uint8),
            bias.astype(np.float32),
            scales.astype(np.float32),
            zero_point.astype(np.uint8),
            k,
            n,
            block_size,
            bias_enable,
            asymmetric_quant,
            mladf_version,
        )
    except RuntimeError:
        print(f"{node.name} failed to generate NPU prepacked weights")
        raise

    suffix = ".preformat"

    return (
        onnx.numpy_helper.from_array(
            new_weight.astype(np.int8).reshape((k, n)), node.input[start_index] + suffix
        ),
        onnx.numpy_helper.from_array(new_bias, bias_name + suffix),
        onnx.numpy_helper.from_array(new_scales, node.input[start_index + 1] + suffix),
        onnx.numpy_helper.from_array(
            new_zeros.astype(np.int8),
            node.input[start_index + 2] + suffix,
        ),
    )


def preprocess_matmulnbits_packed_weights(
    node, start_index, extractor, k, n, block_size, bias_offset
):
    (weight, scales, zero_point, bias, asymmetric_quant, mladf_version) = (
        _extract_arrays(node, start_index, extractor, n, bias_offset)
    )
    bias_enable = bias_offset is not None

    try:
        packed_weight: np.ndarray = matmulnbits.matmulnbits_pack_const_float32(
            weight.astype(np.uint8),
            bias.astype(np.float32),
            scales.astype(np.float32),
            zero_point.astype(np.uint8),
            k,
            n,
            block_size,
            bias_enable,
            asymmetric_quant,
            mladf_version,
        )
    except RuntimeError:
        print(f"{node.name} failed to generate NPU prepacked weights")
        raise

    packed_weight_name = node.input[start_index] + ".packed"
    packed_weight_tensor = onnx.helper.make_tensor(
        packed_weight_name,
        onnx.TensorProto.INT8,
        packed_weight.shape,
        packed_weight.tobytes(),
        True,
    )

    return packed_weight_tensor
