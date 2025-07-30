# Copyright (c) 2024 Advanced Micro Devices, Inc.

import importlib.util
import string
import sys
from pathlib import Path

import ml_dtypes
import numpy as np
import onnx
import onnx_tool
import onnxruntime as ort

import ryzenai_onnx_utils


def get_np_dtype(onnx_type_str):
    """
    Map ONNX type string to a NumPy dtype.
    This function handles common types. Modify as needed.
    """
    ort_type_to_np = {
        "tensor(float)": np.float32,
        "tensor(double)": np.float64,
        "tensor(int8)": np.int8,
        "tensor(int16)": np.int16,
        "tensor(int32)": np.int32,
        "tensor(int64)": np.int64,
        "tensor(uint8)": np.uint8,
        "tensor(uint16)": np.uint16,
    }

    return ort_type_to_np[onnx_type_str]


def create_dummy_inputs(session):
    """
    For each input in the ONNX model, extract the name, shape, and type,
    then create a dummy NumPy tensor.
    """
    dummy_inputs = {}
    for inp in session.get_inputs():
        name = inp.name
        shape = inp.shape
        # Some dimensions can be dynamic (None or -1), replace them with 1
        fixed_shape = [dim if isinstance(dim, int) and dim > 0 else 1 for dim in shape]
        dtype = get_np_dtype(inp.type)
        dummy_tensor = np.random.random(fixed_shape).astype(dtype)
        dummy_inputs[name] = dummy_tensor
        print(f"Input: {name} | Shape: {fixed_shape} | Dtype: {dtype}")
    return dummy_inputs


def run_onnx_model_with_dummy_inputs(
    model_path: Path, provider: str = "DmlExecutionProvider", sess_option=None
):
    """
    Run an ONNX model with DD on NPU.
    """
    # Create an ONNX Runtime session
    session = ort.InferenceSession(
        model_path, sess_option=sess_option, providers=[provider]
    )

    # Create dummy inputs based on the model's expected input shapes
    dummy_inputs = create_dummy_inputs(session)

    # Run the model with the dummy inputs
    outputs = session.run(None, dummy_inputs)
    print("Model outputs:")
    for idx, output in enumerate(outputs):
        print(f"Output {idx}: shape = {output.shape}")


def get_valid_filename(name):
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    return "".join(c for c in name if c in valid_chars)


def float_tensor_to_bfloat_tensor(tensor: onnx.TensorProto, flatten=False):
    assert (
        onnx_tool.tensor.onnxdtype2npdtype(tensor.data_type) is not None
    ), "Unsupported type by onnx_tool"
    np_f = onnx_tool.tensor.tensorproto2ndarray(tensor)
    return float_numpy_to_bfloat_tensor(np_f, tensor.name + ".bfloat16", flatten)


def float_numpy_to_bfloat_tensor(np_array: np.ndarray, tensor_name: str, flatten=False):
    np_f = np_array.flatten() if flatten else np_array
    np_bf = np_f.astype(ml_dtypes.bfloat16)
    return onnx.helper.make_tensor(
        tensor_name, onnx.TensorProto.BFLOAT16, np_bf.shape, np_bf
    )


def transpose_tensor(tensor: onnx.TensorProto, new_axes: list):
    assert (
        onnx_tool.tensor.onnxdtype2npdtype(tensor.data_type) is not None
    ), "Unsupported type by onnx_tool"
    np_f = onnx_tool.tensor.tensorproto2ndarray(tensor).transpose(new_axes)
    return onnx.helper.make_tensor(
        tensor.name + ".transpose", tensor.data_type, np_f.shape, np_f
    )


def get_rng():
    seed = 123
    return np.random.default_rng(seed)


def validate_io_num(io, io_num, label):
    if len(io) != io_num:
        raise ValueError(f"Number of {label} must be {io_num}, not {len(io)}")


def get_rng_data(tvis, lows, highs):
    if not isinstance(lows, list):
        lows = [lows] * len(tvis)
    if not isinstance(highs, list):
        highs = [highs] * len(tvis)

    rng = get_rng()
    rng_data = {}
    for tvi, low, high in zip(tvis, lows, highs):
        shape = ryzenai_onnx_utils.matcher.get_shape(tvi)
        dtype = tvi.type.tensor_type.elem_type
        if dtype == onnx.TensorProto.FLOAT:
            data = rng.uniform(low, high, shape).astype(np.float32)
        elif dtype == onnx.TensorProto.FLOAT16:
            data = rng.uniform(low, high, shape).astype(np.float16)
        else:
            raise ValueError(f"Unhandled type: {dtype}")
        rng_data[tvi.name] = data
    return rng_data


def load_module_from_file(file_name: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, file_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
