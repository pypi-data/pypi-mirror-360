# Copyright (c) 2024 Advanced Micro Devices, Inc.

import json
import math
import os
from pathlib import Path

import onnx
import ryzenai_dynamic_dispatch as dd

import ryzenai_onnx_utils.matcher
import ryzenai_onnx_utils.utils
from ryzenai_onnx_utils.matcher import add_attribute, delete_attribute


def build_dd_node(
    extractor,
    subgraph,
    params: ryzenai_onnx_utils.ReplaceParams,
    extra_outputs=None,
    op_name=None,
    extra_attributes=None,
):
    include_global_inputs = True
    include_initializers = False
    inputs = ryzenai_onnx_utils.matcher.find_inputs_by_nodes(
        subgraph, extractor, include_global_inputs, include_initializers
    )
    input_shapes = ryzenai_onnx_utils.matcher.get_shapes(inputs, extractor)

    include_global_outputs = True
    outputs = ryzenai_onnx_utils.matcher.find_outputs_by_nodes(
        subgraph, extractor.graph, include_global_outputs, extra_outputs
    )
    output_shapes = ryzenai_onnx_utils.matcher.get_shapes(outputs, extractor)

    intermediates = ryzenai_onnx_utils.matcher.find_intermediates_by_nodes(subgraph)

    domain = params.get_subgraph_domain(subgraph)
    xclbin = params.get_subgraph_xclbin(subgraph)

    inputs_num = len(inputs)
    outputs_num = len(outputs)

    filename = ryzenai_onnx_utils.utils.get_valid_filename(subgraph[0].name)
    if not filename:
        raise ValueError("Cannot use an empty filename: node has no name")
    if op_name is None:
        op_name = "DynamicDispatch"
    dd_node = onnx.helper.make_node(
        op_name,
        inputs=inputs,
        outputs=outputs,
        domain=domain,
        name=filename,
    )

    assert len(input_shapes) == inputs_num
    assert len(output_shapes) == outputs_num

    bfp_data = {}
    for node in subgraph:
        bfp16_tensors = []
        bfp16_shapes = []
        attrs_to_delete = []

        try:
            bfp16_tensors = onnx.helper.get_node_attr_value(node, "bfp16_tensors")
            bfp16_tensors = [x.decode("utf-8") for x in bfp16_tensors]
            attrs_to_delete.append("bfp16_tensors")
        except ValueError:
            continue
        for i in range(len(bfp16_tensors)):
            bfp16_shapes.append(
                onnx.helper.get_node_attr_value(node, f"bfp16_shape_{i}")
            )
            attrs_to_delete.append(f"bfp16_shape_{i}")
        for attr in attrs_to_delete:
            delete_attribute(node, attr)

        for bfp_tensor, bfp16_shape in zip(bfp16_tensors, bfp16_shapes):
            bfp_data[bfp_tensor] = bfp16_shape

    for index, input_name in enumerate(inputs):
        if input_name in bfp_data:
            input_shapes[index] = [int(math.prod(bfp_data[input_name]) / 8 * 9)]

    for index, output_name in enumerate(outputs):
        if output_name in bfp_data:
            output_shapes[index] = [int(math.prod(bfp_data[output_name]) / 8 * 9)]

    for i in range(inputs_num):
        add_attribute(dd_node, f"input_shape_{i}", input_shapes[i])
    for i in range(outputs_num):
        add_attribute(dd_node, f"output_shape_{i}", output_shapes[i])

    add_attribute(dd_node, "xclbin", xclbin)
    if extra_attributes is None:
        extra_attributes = {}
    for attribute_name, attribute in extra_attributes.items():
        add_attribute(dd_node, attribute_name, attribute)
    add_attribute(dd_node, "replaced", [x.name for x in subgraph])

    old_initializers = ryzenai_onnx_utils.matcher.find_initializers_by_nodes(
        extractor, subgraph
    )
    input_tvis = ryzenai_onnx_utils.matcher.find_input_tvis_by_nodes(
        extractor, subgraph, inputs
    )
    intermediate_tvis = ryzenai_onnx_utils.matcher.find_input_tvis_by_nodes(
        extractor, subgraph, intermediates
    )
    output_tvis = ryzenai_onnx_utils.matcher.find_output_tvis_by_nodes(
        extractor, subgraph, outputs
    )
    graph_dd = onnx.helper.make_graph(
        subgraph,
        "DD",
        input_tvis,
        output_tvis,
        initializer=old_initializers,
        value_info=intermediate_tvis,
    )

    aux_info = {}
    if "is_llm" in params.attributes:
        aux_info["is_llm"] = True
    graph = dd.onnx_graph.ONNXGraph(graph_dd, aux_info)

    prefix = f"{filename}_"
    use_abs_path = False
    metainfo = dd.fuse.prepare_metadata(
        graph, params.dd_files_path, prefix, use_abs_path
    )
    assert len(metainfo) in [4, 5]

    # this is to handle DD versions without the state table
    tensor_map = metainfo[3] if len(metainfo) == 5 else metainfo[2]

    # for bfp16 type, we can't save it as a type in ONNX nor does DD recognize it
    # so we have to do this hack afterwards to update the type and restore the
    # original shape of the data
    for tensor, shape in bfp_data.items():
        tensor_map[tensor]["dtype"] = "bfp16ebs8"
        tensor_map[tensor]["shape"] = shape

    # this hack is needed because DD doesn't differentiate between the path it saves
    # files to and the path that it saves in the JSON metadata if the dd_files_path
    # is relative
    if (
        not params.dd_files_path.is_absolute()
        and params.dd_files_path.absolute() != params.abs_dd_files_path
    ):
        const_tensors = graph.getConstTensors()
        const_file_info = graph.writeConsts(
            const_tensors, params.abs_dd_files_path, prefix, use_abs_path
        )
        for _key, (file_path, _file_size) in const_file_info.items():
            local_file_path = params.dd_files_path / Path(file_path).name
            local_file_path.unlink()

    meta_json_name = params.abs_dd_files_path / f"{filename}_meta.json"
    dd.fuse.save_tensors_to_json(meta_json_name, *metainfo)

    return dd_node


def write_to_bin(file_name, file_size, bin_file):
    with open(file_name, "rb") as f:
        bin_data = f.read()
    with open(bin_file, "ab") as f:
        f.seek(0, os.SEEK_END)
        initial_size = f.tell()
        f.write(bin_data)
        f.seek(0, os.SEEK_END)
        new_size = f.tell()
        assert new_size == initial_size + file_size
    return initial_size


def combine_dd(dd_files_path: Path, dd_files_path_abs: Path, output_path: Path):
    all_json_paths = dd_files_path_abs.glob("*.json")
    super_json = {}
    bin_file_name = "meta.bin"
    bin_file = dd_files_path_abs / bin_file_name
    bin_file_str = str(dd_files_path / bin_file_name)
    for json_path in all_json_paths:
        with open(json_path) as f:
            meta_json = json.load(f)
        tensor_map = meta_json["tensor_map"]
        for _, args in tensor_map.items():
            if "file_name" in args:
                file_name = Path(args["file_name"])
                if not file_name.is_absolute():
                    file_name = output_path / file_name
                file_size = args["file_size"]
                file_offset = write_to_bin(file_name, file_size, bin_file)
                args["file_offset"] = file_offset
                args["file_name"] = bin_file_str
                os.remove(file_name)

        super_json[json_path.stem.removesuffix("_meta")] = meta_json
        os.remove(json_path)

    if super_json:
        with open(dd_files_path_abs / "meta.json", "w") as f:
            json.dump(super_json, f, indent=None, separators=(",", ":"))
