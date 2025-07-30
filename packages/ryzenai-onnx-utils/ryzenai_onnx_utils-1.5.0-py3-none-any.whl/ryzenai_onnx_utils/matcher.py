# Copyright (c) 2023 Zyy
# Modification Copyright (c) 2024 Advanced Micro Devices, Inc.
# Licensed under the MIT License.

import copy
import inspect
import itertools
import os
from pathlib import Path
from typing import Optional, Union

import ml_dtypes
import numpy as np
import onnx
import onnx.external_data_helper
import onnx.onnx_cpp2py_export.checker as c_checker
from onnx import _get_serializer, _save_bytes

import ryzenai_onnx_utils.matcher

from .lexer import Lexer


def configure_parser(subparser):
    matcher_parser = subparser.add_parser("match")
    matcher_parser.add_argument(
        "input_path", type=Path, help="Path to input ONNX model"
    )
    matcher_parser.add_argument(
        "--strategy", type=Path, help="Strategy to run before extracting pattern"
    )
    matcher_parser.add_argument(
        "--extract-inputs",
        type=str,
        nargs="*",
        help="Optionally extract from these inputs",
    )
    matcher_parser.add_argument(
        "--extract-outputs",
        type=str,
        nargs="*",
        help="Optionally extract from these outputs",
    )
    matcher_parser.add_argument(
        "--load-external-data",
        action="store_true",
        help="Load all external data at startup",
    )
    matcher_parser.add_argument(
        "--hints-key",
        default=None,
        nargs="*",
        help="Key to use for dynamic passes",
    )

    return matcher_parser


class ReplaceParams:
    """
    Extra arguments that are passed to the replace function from the top-level
    """

    def __init__(self, attributes, output_path, dd_files_path, abs_dd_files_path):
        self.attributes: dict = attributes
        self.output_path = output_path
        self.dd_files_path: Path = dd_files_path
        self.abs_dd_files_path: Path = abs_dd_files_path

    def get_domain(self, name):
        return self._get_property("domains", name)

    def get_domains(self):
        return self._get_properties("domains")

    def get_xclbin(self, name):
        return self._get_property("xclbins", name)

    def get_op_namespace(self, name):
        return self._get_property("op_namespaces", name)

    def get_op_namespaces(self):
        return self._get_properties("op_namespaces")

    def get_subgraph_domain(self, subgraph: list[onnx.NodeProto]):
        """
        Given a subgraph of nodes, validate that they all share the same domain
        and return this domain

        Args:
            subgraph (list[onnx.NodeProto]): subgraph to get domain for
        """
        return self._get_subgraph_property("domains", subgraph)

    def get_subgraph_xclbin(self, subgraph: list[onnx.NodeProto]):
        """
        Given a subgraph of nodes, validate that they all share the same xclbin
        and return this xclbin

        Args:
            subgraph (list[onnx.NodeProto]): subgraph to get xclbin for
        """
        return self._get_subgraph_property("xclbins", subgraph)

    def get_subgraph_op_namespace(self, subgraph: list[onnx.NodeProto]):
        """
        Given a subgraph of nodes, validate that they all share the same op
        namespace and return this namespace

        Args:
            subgraph (list[onnx.NodeProto]): subgraph to get op_namespace for
        """
        return self._get_subgraph_property("op_namespaces", subgraph)

    def get_bool_attr(self, attr_name, default_value=None):
        if default_value is None:
            assert attr_name in self.attributes
        value = self.attributes.get(attr_name, default_value)
        if isinstance(value, bool):
            return value
        assert isinstance(value, str)
        value = value.lower()
        return value in {"true", "yes", "on", "y"}

    def _get_subgraph_property(self, prop_name, subgraph: list[onnx.NodeProto]):
        prop = None
        for node in subgraph:
            new_prop = self._get_property(prop_name, node.op_type)
            if prop is None:
                prop = new_prop
            elif new_prop != prop:
                raise ValueError(
                    f"Multiple {prop_name}s detected in subgraph: {prop} and {new_prop}"
                )
            # else case they match so nothing to do
        return prop

    def _get_property(self, prop_name, key):
        prop = self.attributes[prop_name]
        if isinstance(prop, str):
            return prop
        if isinstance(prop, (str, int, float)):
            if key in prop:
                return prop[key]
            if "*" in prop:
                return prop["*"]
        raise ValueError(f"Unsupported {prop_name} type saved or unhandled key {key}")

    def _get_properties(self, prop_name):
        prop = self.attributes[prop_name]
        if isinstance(prop, (str, int, float)):
            return [prop]
        if isinstance(prop, dict):
            props = set()
            for _key, value in prop.items():
                props.add(value)
            return list(props)
        raise ValueError(f"Unsupported {prop_name} type saved")


def log(msg):
    lineno = inspect.stack()[1].lineno
    print(f"[Matcher:{lineno}]: {msg}")


def input_name_from_node_name(node_name, suffix):
    input_name = (
        node_name[1:].replace("/", ".")
        if node_name.startswith(("/", "."))
        else node_name.replace("/", ".")
    )
    input_name += f".{suffix}"
    return input_name


def find_nodes_by_input(input_name: str, graph: onnx.GraphProto, reverse=False):
    nodes = []
    for node in graph.node:
        if node.op_type == "Constant":
            continue

        if input_name in node.input:
            nodes.append(node)
    if reverse:
        nodes.reverse()
    return nodes


def is_used_input(input_name: str, graph: onnx.GraphProto) -> bool:
    for node in graph.node:
        if input_name in node.input:
            return True

        if node.op_type in {"Scan", "If", "Loop"}:
            for attr in node.attribute:
                subgraphs = []
                if attr.type == onnx.AttributeProto.GRAPH:
                    subgraphs = [attr.g]
                elif attr.type == onnx.AttributeProto.GRAPHS:
                    subgraphs = attr.graphs
                for subgraph in subgraphs:
                    if input_name in [input_tvi.name for input_tvi in graph.input]:
                        return True
                    if is_used_input(input_name, subgraph):
                        return True
    return False


def is_used_initializer(input_name: str, graph: onnx.GraphProto) -> bool:
    if is_used_input(input_name, graph):
        return True

    def recurse(subgraph: onnx.GraphProto):
        if input_name in [o.name for o in subgraph.output]:
            return True

        for node in subgraph.node:
            if node.op_type in {"Scan", "If", "Loop"}:
                for attr in node.attribute:
                    subgraphs = []
                    if attr.type == onnx.AttributeProto.GRAPH:
                        subgraphs = [attr.g]
                    elif attr.type == onnx.AttributeProto.GRAPHS:
                        subgraphs = attr.graphs
                    for subgraph in subgraphs:
                        if recurse(subgraph):
                            return True
        return False

    return recurse(graph)


def find_nodes_by_output(output_name: str, graph: onnx.GraphProto):
    nodes: list[onnx.NodeProto] = []
    for node in graph.node:
        if node.op_type == "Constant":
            continue

        if output_name in node.output:
            nodes.append(node)
    return nodes


def build_input_map(
    graph_or_extractor: Union[onnx.GraphProto, onnx.utils.Extractor],
    exclude_initializers=True,
):
    input_map = {}
    if isinstance(graph_or_extractor, onnx.GraphProto):
        nodes = graph_or_extractor.node
    else:
        nodes = graph_or_extractor.graph.node
    for index, node in enumerate(nodes):
        for input_name in node.input:
            if not exclude_initializers or (
                exclude_initializers
                and not is_initializer(input_name, graph_or_extractor)
            ):
                if input_name not in input_map:
                    input_map[input_name] = []
                input_map[input_name].append(index)
    return input_map


def build_output_map(graph: onnx.GraphProto):
    output_map = {}
    for index, node in enumerate(graph.node):
        for output_name in node.output:
            if output_name not in output_map:
                output_map[output_name] = []
            output_map[output_name].append(index)
    return output_map


def find_consts(name: str, graph: onnx.GraphProto):
    nodes = []
    for node in graph.node:
        if name in node.output and node.op_type == "Constant":
            nodes.append(node)
    return nodes


def find_input(name: str, graph: onnx.GraphProto):
    for input_tensor in graph.input:
        if input_tensor.name == name:
            return input_tensor
    return None


def find_output(name: str, graph: onnx.GraphProto):
    for output_tensor in graph.output:
        if output_tensor.name == name:
            return output_tensor
    return None


def is_input_edge(name: str, graph: onnx.GraphProto):
    return any(input_tensor.name == name for input_tensor in graph.input)


def is_output_edge(name: str, graph: onnx.GraphProto):
    return any(output_tensor.name == name for output_tensor in graph.output)


def is_output_edge_or_adjacent(name: str, graph: onnx.GraphProto):
    """
    Check if an edge is a direct output edge or feeds into one of a set of
    operators whose output is an output edge

    Args:
        name (str): Name of the edge
        graph (onnx.GraphProto): ONNX graph object
    """

    output_edges = [x.name for x in graph.output]

    child_nodes = find_nodes_by_input(name, graph)
    for node in child_nodes:
        if node.op_type in ["Cast", "CastAvx"] and is_output_edge(
            node.output[0], graph
        ):
            output_edges.append(node.input[0])

    return any(name == x for x in output_edges)


def get_shapes(objs: list, extractor=None):
    shapes = []
    for obj in objs:
        shapes.append(get_shape(obj, extractor))
    return shapes


def get_shape(obj, extractor: onnx.utils.Extractor = None):
    if isinstance(obj, onnx.ValueInfoProto):
        if not obj.type.tensor_type.shape.dim:
            return tuple([1])
        shape = []
        for d in obj.type.tensor_type.shape.dim:
            if d.dim_value < 1:
                shape.append(d.dim_param)
            else:
                shape.append(d.dim_value)
        return tuple(shape)
    if isinstance(obj, onnx.TensorProto):
        if not obj.dims:
            return tuple([1])
        return tuple(obj.dims)
    if isinstance(obj, str):
        assert extractor is not None
        if is_initializer(obj, extractor):
            obj = get_initializer(obj, extractor, False)
        elif obj in extractor.vimap:
            obj = extractor.vimap[obj]
        elif find_input(obj, extractor.graph) is not None:
            obj = find_input(obj, extractor.graph)
        elif find_output(obj, extractor.graph) is not None:
            obj = find_output(obj, extractor.graph)
        else:
            raise ValueError(f"Cannot interpret {obj} as valid input for get_shape()")
        return get_shape(obj)
    raise ValueError(f"Unsupported type: {type(obj)}")


def get_dtype(name, extractor: onnx.utils.Extractor):
    """Extract the dtype of a named tensor/weight

    Args:
        name (str): Name of the tensor
        extractor (onnx.utils.Extractor): The extractor is used to query the dtype

    Raises:
        ValueError: Raised if nothing is found

    Returns:
        int: The type as an integer defined in ONNX
    """
    if name in extractor.vimap:
        return extractor.vimap[name].type.tensor_type.elem_type
    if name in extractor.wmap:
        return extractor.wmap[name].data_type
    found_input = [x for x in extractor.graph.input if x.name == name]
    if len(found_input) == 1:
        return found_input[0].type.tensor_type.elem_type
    found_output = [x for x in extractor.graph.output if x.name == name]
    if len(found_output) == 1:
        return found_output[0].type.tensor_type.elem_type
    raise ValueError(f"{name} not found in graph")


def get_dtype_str(name, extractor):
    """Extract the dtype of a named weight/tensor as a string

    Args:
        name (str): Name of the tensor
        extractor (onnx.utils.Extractor): The extractor is used to query the dtype

    Returns:
        str: The string representation of the type
    """
    return onnx.helper.tensor_dtype_to_string(get_dtype(name, extractor))


def set_external_data(
    tensor: onnx.TensorProto,
    location: str,
    offset: Optional[int] = None,
    length: Optional[int] = None,
    checksum: Optional[str] = None,
    basepath: Optional[str] = None,
) -> None:
    """
    This is a copy of the same named function in onnx.external_data_helper.py
    but it doesn't require raw_data to be set. For memory reasons, tensors may
    not have loaded weights when this function is called.
    """

    del tensor.external_data[:]
    tensor.data_location = onnx.TensorProto.EXTERNAL
    for k, v in {
        "location": location,
        "offset": int(offset) if offset is not None else None,
        "length": int(length) if length is not None else None,
        "checksum": checksum,
        "basepath": basepath,
    }.items():
        if v is not None:
            entry = tensor.external_data.add()
            entry.key = k
            entry.value = str(v)


def load_external_data_for_tensor(
    tensor: onnx.TensorProto, external_data_file_path, offset, length
) -> None:
    """Loads data from an external file for tensor.
    Ideally TensorProto should not hold any raw data but if it does it will be ignored.

    Arguments:
        tensor: a TensorProto object.
        base_dir: directory that contains the external data.
    """
    with open(external_data_file_path, "rb") as data_file:
        if offset:
            data_file.seek(offset)

        if length:
            tensor.raw_data = data_file.read(length)
        else:
            tensor.raw_data = data_file.read()


def parse_external_data(tensor: onnx.TensorProto):
    external_data = {}
    for item in tensor.external_data:
        value = int(item.value) if item.key in ["offset", "length"] else item.value
        external_data[item.key] = value
    return external_data


def get_external_data_for_tensor(tensor: onnx.TensorProto, base_dir: str) -> bytes:
    """Loads data from an external file for tensor.
    Ideally TensorProto should not hold any raw data but if it does it will be ignored.

    This is a copy of a similar function in onnx.external_data_helper but it just
    returns the data rather than setting the tensor's raw data

    Arguments:
        tensor: a TensorProto object.
        base_dir: directory that contains the external data.
    """
    info = onnx.external_data_helper.ExternalDataInfo(tensor)
    external_data_file_path = c_checker._resolve_external_data_location(  # type: ignore[attr-defined]
        base_dir, info.location, tensor.name
    )

    with open(external_data_file_path, "rb") as data_file:
        if info.offset:
            data_file.seek(info.offset)

        data = data_file.read(info.length) if info.length else data_file.read()
    return data


def load_tensor(name, extractor: onnx.utils.Extractor):
    tensor = extractor.wmap[name]
    info = onnx.external_data_helper.ExternalDataInfo(tensor)
    if not info.location:
        # no external data
        return
    if name in extractor.wmap_loaded:
        return
    props = extractor.model.metadata_props
    path = None
    for prop in props:
        if prop.key == "onnx_utils_load":
            path = prop.value
    if path:
        assert is_initializer(name, extractor)
        tensor.raw_data = get_external_data_for_tensor(tensor, path)
        extractor.wmap_loaded.add(name)


def add_attribute(node: onnx.NodeProto, key: str, value, attr_type=None):
    node.attribute.append(onnx.helper.make_attribute(key, value, attr_type=attr_type))


def get_attribute(node: onnx.NodeProto, key: str, default_value=None):
    try:
        return onnx.helper.get_node_attr_value(node, key)
    except ValueError:
        if default_value is not None:
            return default_value
        raise


def has_attribute(node: onnx.NodeProto, key: str):
    try:
        onnx.helper.get_node_attr_value(node, key)
    except ValueError:
        return False
    else:
        return True


def delete_attribute(node: onnx.NodeProto, key: str):
    index = None
    for i, attr in enumerate(node.attribute):
        if attr.name == key:
            index = i
            break
    if index is not None:
        del node.attribute[index]


def set_attribute(node: onnx.NodeProto, key: str, value):
    delete_attribute(node, key)
    add_attribute(node, key, value)


def copy_attributes(src_node: onnx.NodeProto, dst_node: onnx.NodeProto):
    dst_node.attribute.extend(src_node.attribute)


def set_value_in_attribute(node: onnx.NodeProto, attr_key, original_value, new_value):
    values = onnx.helper.get_node_attr_value(node, attr_key)
    assert isinstance(values, list), f"Attribute {attr_key} is not a list"
    if isinstance(values[0], bytes):
        values = [x.decode("utf-8") for x in values]
    index = None
    for i, value in enumerate(values):
        if value == original_value:
            index = i
            break
    if index is not None:
        values[i] = new_value
        set_attribute(node, attr_key, values)


def append_value_in_attribute(node: onnx.NodeProto, attr_key, value):
    try:
        values = onnx.helper.get_node_attr_value(node, attr_key)
    except ValueError:
        set_attribute(node, attr_key, [value])
        return
    assert isinstance(values, list), f"Attribute {attr_key} is not a list"
    if isinstance(values[0], bytes):
        values = [x.decode("utf-8") for x in values]
    if isinstance(value, list):
        values.extend(value)
    else:
        values.append(value)
    set_attribute(node, attr_key, values)


def is_initializer(
    name: str, graph_or_extractor: Union[onnx.utils.Extractor, onnx.GraphProto]
):
    if isinstance(graph_or_extractor, onnx.utils.Extractor):
        return name in graph_or_extractor.wmap
    for initializer in graph_or_extractor.initializer:
        if initializer.name == name:
            return True
    return False


def get_initializer(
    initializer_name: str,
    graph_or_extractor: Union[onnx.GraphProto, onnx.utils.Extractor],
    load=True,
):
    if isinstance(graph_or_extractor, onnx.utils.Extractor):
        if load:
            load_tensor(initializer_name, graph_or_extractor)
        return graph_or_extractor.wmap[initializer_name]
    else:
        for initializer in graph_or_extractor.initializer:
            if initializer.name == initializer_name:
                return initializer
        raise ValueError(f"Initializer {initializer_name} not found")


def get_initializer_as_numpy(name, extractor: onnx.utils.Extractor, do_reshape=True):
    tensor = extractor.wmap[name]
    info = onnx.external_data_helper.ExternalDataInfo(tensor)
    if not info.location or name in extractor.wmap_loaded:
        if tensor.data_type == onnx.TensorProto.BFLOAT16:
            return np.frombuffer(tensor.raw_data, dtype=ml_dtypes.bfloat16)
        elif tensor.data_type == onnx.TensorProto.INT4:
            # For INT4, onnx.numpy_helper.to_array is very slow
            # and we only need the data returned as UINT8. So
            # np.frombuffer(tensor.raw_data, dtype=np.uint8) would be
            # enough.
            return np.frombuffer(tensor.raw_data, dtype=np.uint8)
        else:
            return onnx.numpy_helper.to_array(tensor)

    path = os.getcwd()
    try:
        props = extractor.model.metadata_props
        for prop in props:
            if prop.key == "onnx_utils_load":
                path = prop.value
    except AttributeError:
        # if the extractor was loaded with just the graph, there's no model
        # so assume path is fine as the working directory
        if extractor.model is not None:
            raise
    assert is_initializer(name, extractor)
    data = get_external_data_for_tensor(tensor, path)
    np_dtype = onnx.helper.tensor_dtype_to_np_dtype(tensor.data_type)
    if tensor.data_type == onnx.TensorProto.BFLOAT16:
        np_dtype = ml_dtypes.bfloat16
    elif tensor.data_type == onnx.TensorProto.INT4:
        # INT4 data is read as UINT8
        np_dtype = np.uint8

    if do_reshape:
        assert tensor.data_type != onnx.TensorProto.INT4
        shape = get_shape(tensor)
        return np.frombuffer(data, dtype=np_dtype).reshape(shape)
    else:
        return np.frombuffer(data, dtype=np_dtype)


def convert_to_external(
    input_path: Path,
    output_path: Path,
    external_data_extension: str,
    size_threshold=1024,
):
    stem = output_path.stem
    location = f"{stem}.{external_data_extension}"
    extractor = load_extractor(input_path, False)
    for index, init in enumerate(extractor.graph.initializer):
        if not init.raw_data:
            np_array = get_initializer_as_numpy(init.name, extractor, do_reshape=False)
            extractor.graph.initializer[index].raw_data = np_array.tobytes()
        # onnx.external_data_helper.set_external_data(extractor.graph.initializer[index], location)
    ((input_path.parent) / location).unlink(True)

    onnx.external_data_helper.convert_model_to_external_data(
        extractor.model, location=location, size_threshold=size_threshold
    )
    onnx.save_model(
        extractor.model, output_path, save_as_external_data=True, location=location
    )


def get_external_data_name(graph: onnx.GraphProto):
    for tensor in graph.initializer:
        if onnx.external_data_helper.uses_external_data(tensor):
            return onnx.external_data_helper.ExternalDataInfo(tensor).location
    return ""


def save_external_data(tensor: onnx.TensorProto, base_path: str, data: bytes) -> None:
    """This is a copy of the same function from ORT but where it doesn't require
    raw data to exist in the tensor. The data to set is passed externally

    Arguments:
        tensor (TensorProto): Tensor object to be serialized
        base_path: System path of a folder where tensor data is to be stored
        data (bytes): Data to write
    """

    info = onnx.external_data_helper.ExternalDataInfo(tensor)
    external_data_file_path = Path(base_path) / info.location
    assert info.location

    external_data_file_path.touch(exist_ok=True)

    # Open file for reading and writing at random locations ('r+b')
    with open(external_data_file_path, "r+b") as data_file:
        data_file.seek(0, 2)
        if info.offset is not None:
            # Pad file to required offset if needed
            file_size = data_file.tell()
            if info.offset > file_size:
                data_file.write(b"\0" * (info.offset - file_size))

            data_file.seek(info.offset)
        offset = data_file.tell()
        data_file.write(data)
        set_external_data(tensor, info.location, offset, data_file.tell() - offset)


def save_external_data_with_extractor(
    model: onnx.ModelProto,
    extractor: onnx.utils.Extractor,
    external_data_name: str,
    output_path: Path,
    save_as_external: bool,
    alias_shared_tensors: bool = False,
):
    (output_path / external_data_name).unlink(True)
    # default minimum size threshold for moving tensor to external
    size_threshold = 1024
    offset = 0
    tensor_addresses: dict[str, tuple] = {}

    def append_external_data(
        extractor: onnx.utils.Extractor,
        external_data_name: str,
        output_path: Path,
        save_as_external: bool,
        offset: int,
    ):
        unused_inits = []
        inits = []
        for init_name, init in extractor.wmap.items():
            if is_used_initializer(init.name, extractor.model.graph):
                np_data = get_initializer_as_numpy(
                    init_name, extractor, do_reshape=False
                )
                length = np_data.size * np_data.itemsize
                if length > size_threshold and save_as_external:
                    init.ClearField("raw_data")
                    if alias_shared_tensors and init_name in tensor_addresses:
                        saved_length = tensor_addresses[init_name][1]
                        saved_dtype = tensor_addresses[init_name][2]

                        assert saved_length == length
                        assert saved_dtype == np_data.dtype
                        set_external_data(
                            init,
                            external_data_name,
                            tensor_addresses[init_name][0],
                            length,
                        )
                    else:
                        if alias_shared_tensors:
                            tensor_addresses[init_name] = (
                                offset,
                                length,
                                np_data.dtype,
                            )
                        set_external_data(
                            init,
                            external_data_name,
                            offset,
                            length,
                        )
                        offset += length
                    save_external_data(init, output_path, np_data.tobytes())
                    model.graph.initializer.append(init)
                    inits.append(init)
                else:
                    load_tensor(init_name, extractor)
                    del init.external_data[:]
                    init.data_location = onnx.TensorProto.DEFAULT
                    model.graph.initializer.append(init)
                    inits.append(init)
            else:
                unused_inits.append(init_name)
        for init_name in unused_inits:
            del extractor.wmap[init_name]
        return inits, offset

    def recurse(subgraph: onnx.GraphProto, offset: int):
        sub_model = onnx.helper.make_model(subgraph, producer_name="from_subgraph")
        sub_extractor = ryzenai_onnx_utils.matcher.get_extractor(sub_model)
        del subgraph.initializer[:]
        inits, offset = append_external_data(
            sub_extractor,
            external_data_name,
            output_path,
            save_as_external,
            offset,
        )
        subgraph.initializer.extend(inits)
        return offset

    for node in model.graph.node:
        for attr in node.attribute:
            if attr.type == onnx.AttributeProto.GRAPH:
                offset = recurse(attr.g, offset)
            elif attr.type == onnx.AttributeProto.GRAPHS:
                for subgraph in attr.graphs:
                    offset = recurse(subgraph, offset)
    del model.graph.initializer[:]
    append_external_data(
        extractor, external_data_name, output_path, save_as_external, offset
    )


def save_model_without_external_data(model: onnx.ModelProto, f: Path):
    """
    This is a snippet of onnx.save_model but only the part that serializes the
    onnx model, assuming the external data has already been saved with
    save_external_data_with_extractor()
    Args:
        model (onnx.ModelProto): Model to save
        f (Path): Path to save it to
    """
    serialized = _get_serializer(None, f).serialize_proto(model)
    _save_bytes(serialized, f)


def delete_model(model_path: Path, external_data_extension):
    model_path.unlink(True)
    model_path.with_suffix(f".{external_data_extension}").unlink(True)
    model_path.with_suffix(".pb.bin").unlink(True)


def get_initializers(names, extractor, load=True):
    if isinstance(names, str):
        names = [names]
    nodes = []
    for name in names:
        if is_initializer(name, extractor):
            nodes.append(get_initializer(name, extractor, load))
    return nodes


def find_initializers_by_nodes(extractor, nodes, load=True):
    if not isinstance(nodes, list):
        nodes = [nodes]

    initializer_names = set()

    for node in nodes:
        for io in itertools.chain(node.input, node.output):
            if is_initializer(io, extractor):
                # if io in model.graph.initializer:
                initializer_names.add(io)
    return get_initializers(initializer_names, extractor, load)


def _find_io_by_nodes(nodes):
    if not isinstance(nodes, list):
        nodes = [nodes]

    inputs = set()
    outputs = set()

    for node in nodes:
        for io in node.input:
            inputs.add(io)
        for io in node.output:
            outputs.add(io)

    return inputs, outputs


def find_inputs_by_nodes(
    nodes,
    graph_or_extractor: Union[onnx.utils.Extractor, onnx.GraphProto] = None,
    include_global_inputs=False,
    include_initializers=True,
):
    if (
        include_global_inputs or not include_initializers
    ) and graph_or_extractor is None:
        raise ValueError(
            "If including global inputs or excluding initializers, an extractor/graph must be provided"
        )

    if isinstance(graph_or_extractor, onnx.utils.Extractor):
        graph = graph_or_extractor.graph
    else:
        graph = graph_or_extractor

    inputs, outputs = _find_io_by_nodes(nodes)
    if include_global_inputs:
        for io in graph.input:
            inputs.add(io.name)
    if not include_initializers:
        initializers = set()
        for io in inputs:
            if is_initializer(io, graph_or_extractor):
                initializers.add(io)
        inputs = inputs - initializers
    real_inputs = inputs - outputs

    inputs_ordered = []
    for node in nodes:
        for io in node.input:
            if io in real_inputs:
                inputs_ordered.append(io)
                real_inputs.remove(io)
    return inputs_ordered


def find_outputs_by_nodes(
    nodes,
    graph: onnx.GraphProto = None,
    include_global_outputs=False,
    extra_outputs=None,
):
    inputs, outputs = _find_io_by_nodes(nodes)
    real_outputs = outputs - inputs
    # have to add these after removing inputs
    if extra_outputs is not None:
        # extra outputs are added at this stage so that when we go to order it
        # below, the extra outputs are in the right order
        if not isinstance(extra_outputs, (tuple, list)):
            extra_outputs = [extra_outputs]
        for output in extra_outputs:
            real_outputs.add(output)
    if include_global_outputs:
        assert graph is not None
        for output in graph.output:
            real_outputs.add(output.name)

    outputs_ordered = []
    for node in nodes:
        for io in node.output:
            if io in real_outputs:
                outputs_ordered.append(io)
                real_outputs.remove(io)
    return outputs_ordered


def find_intermediates_by_nodes(nodes):
    inputs, outputs = _find_io_by_nodes(nodes)
    return list(outputs.intersection(inputs))


def has_multiple_successors(edge, graph: onnx.GraphProto):
    cast_0_successors = find_nodes_by_input(edge, graph)
    multiple_successors = False
    if len(cast_0_successors) > 1 or is_output_edge(edge, graph):
        multiple_successors = True
    return multiple_successors


def find_input_tvis_by_nodes(extractor, nodes, names=None):
    if not isinstance(nodes, list):
        nodes = [nodes]

    tvis = []

    for node in nodes:
        for io in node.input:
            if names is None or io in names:
                if io in extractor.vimap:
                    tvis.append(extractor.vimap[io])
                if is_input_edge(io, extractor.graph):
                    for input_tvi in extractor.graph.input:
                        if input_tvi.name == io:
                            tvis.append(input_tvi)
                            break
    return tvis


def find_output_tvis_by_nodes(extractor, nodes, names=None):
    if not isinstance(nodes, list):
        nodes = [nodes]

    tvis = []

    for node in nodes:
        for io in node.output:
            if names is None or io in names:
                if io in extractor.vimap:
                    tvis.append(extractor.vimap[io])
                if is_output_edge(io, extractor.graph):
                    for output_tvi in extractor.graph.output:
                        if output_tvi.name == io:
                            tvis.append(output_tvi)
                            break
    return tvis


def find_tvis_by_nodes(extractor, nodes):
    if not isinstance(nodes, list):
        nodes = [nodes]

    tvis = []

    for node in nodes:
        for io in itertools.chain(node.input, node.output):
            if io in extractor.vimap:
                tvis.append(extractor.vimap[io])
    return tvis


def set_opset(model, domain, version):
    found = False
    opsets = model.opset_import
    for opset in opsets:
        if opset.domain == domain:
            found = True
            # strictly increase the configured version so the highest value is kept
            if opset.version < version:
                opset.version = version
            break
    if not found:
        model.opset_import.add(domain=domain, version=version)


def _remove_graph_io(names, all_io):
    inputs_to_remove = []
    for index, input_tvi in enumerate(all_io):
        if input_tvi.name in names:
            inputs_to_remove.append(index)
    sorted_indices = sorted(inputs_to_remove, reverse=True)
    for index in sorted_indices:
        del all_io[index]


def remove_graph_inputs(input_names, graph: onnx.GraphProto):
    _remove_graph_io(input_names, graph.input)


def remove_graph_outputs(output_names, graph: onnx.GraphProto):
    _remove_graph_io(output_names, graph.output)


def remove_node_and_init_by_indices(graph: onnx.GraphProto, inodes, inits, tvis):
    inodes = sorted(inodes, reverse=True)
    inits = sorted(inits, reverse=True)
    # tvis = sorted(tvis, reverse=True)
    for i in inodes:
        del graph.node[i]

    for i in inits:
        del graph.initializer[i]

    # for i in tvis:
    #     del model.graph.value_info[i]

    # gc.collect()


def remove_node_and_info(extractor: onnx.utils.Extractor, node):
    model = extractor.model
    node_indices = []
    init_indices = []
    tvi_indices = []
    nodes_list = list(model.graph.node)
    init_list = list(model.graph.initializer)
    # tvis_list = list(model.graph.value_info)
    for input in node.input:
        consts = find_consts(input, model.graph)

        for n in consts:
            users = find_nodes_by_input(n.name, extractor.graph)
            if not len(users):
                node_indices.append(nodes_list.index(n))

        inits = get_initializers(input, extractor, False)
        for n in inits:
            users = find_nodes_by_input(n.name, extractor.graph)
            if not len(users):
                try:
                    init_index = init_list.index(n)
                    init_indices.append(init_index)
                except ValueError:
                    pass

                del extractor.wmap[n.name]

    # tvis = find_tvis_by_nodes(extractor, node)

    # for n in tvis:
    #     try:
    #         tvi_indices.append(tvis_list.index(n))
    #         del extractor.vimap[n.name]
    #     except ValueError:
    #         pass

    remove_node_and_init_by_indices(
        model.graph, node_indices, init_indices, tvi_indices
    )
    # gc.collect()


def graph_topological_sort(extractor: onnx.utils.Extractor, is_deterministic=False):
    """
    Perform a topological sort of the nodes in the ONNX graph. This is a copy of
    a similar named function in onnxruntime, modified to work the extractor.

    Args:
        extractor (onnx.utils.Extractor): Extractor
        is_deterministic (bool, optional): Sort nodes before sort. Defaults to False.

    Raises:
        RuntimeError: raised if graph is not a DAG
    """
    deps_set = set()  # dependency set of all node
    sorted_node_set = set()  # sorted node set
    sorted_nodes = []  # initialize sorted_nodes

    graph = extractor.graph

    initializer_names = [init for init in extractor.wmap]
    graph_input_names = [input.name for input in graph.input]
    input_names = initializer_names + graph_input_names

    if is_deterministic:
        input_names.sort()

    for input_name in input_names:
        deps_set.add(input_name)

    sorted_node_set_len = -1
    graph_nodes = (
        graph.node if not is_deterministic else sorted(graph.node, key=lambda x: x.name)
    )

    last_node_name = None
    while len(sorted_node_set) != len(graph_nodes):
        if len(sorted_node_set) == sorted_node_set_len:
            break
        sorted_node_set_len = len(sorted_node_set)
        for node_idx, node in enumerate(graph_nodes):
            if node_idx in sorted_node_set:
                continue
            input_count = sum(1 for _ in node.input if _)
            if input_count == 0:
                sorted_nodes.append(node)
                sorted_node_set.add(node_idx)
                for output in node.output:
                    if output:
                        deps_set.add(output)
                continue
            failed = False
            for input_name in node.input:
                if input_name and input_name not in deps_set:
                    failed = True
                    last_node_name = node.name
            if not failed:
                sorted_nodes.append(node)
                sorted_node_set.add(node_idx)
                for output in node.output:
                    if output:
                        deps_set.add(output)
            else:
                continue

    if len(sorted_node_set) != len(graph.node):
        raise RuntimeError(
            f"Graph is not a DAG: len(sorted_node_set)={len(sorted_node_set)}, len(graph.node)={len(graph.node)}, failed at node {last_node_name}"
        )

    graph.ClearField("node")
    graph.node.extend(sorted_nodes)


# def cleanup(model):
#     in_graph_tensors = set()
#     already_pass = set()
#     output_names = set([item.name for item in model.graph.output])
#     tensors = [[item.name] for item in model.graph.input]
#     for node in model.graph.node:
#         if len(node.input) == 0:
#             tensors.extend(list(node.output))

#     already_pass_tensors = []
#     while len(tensors) > 0:
#         names = tensors.pop()
#         tensor = names[-1]
#         if tensor in already_pass:
#             already_pass_tensors.append(names)
#             continue

#         already_pass.add(tensor)
#         if tensor in output_names:
#             in_graph_tensors.update(names)
#             continue

#         nodes = find_nodes_by_input(tensor, model.graph)
#         for node in nodes:
#             for output in node.output:
#                 tensors.append(names + list(node.input) + [output])

#     for names in already_pass_tensors:
#         tensor = names[-1]
#         if tensor in in_graph_tensors:
#             in_graph_tensors.update(names)

#     del_nodes = []
#     del_inits = []
#     for inode, node in enumerate(model.graph.node):
#         in_graph = any([output in in_graph_tensors for output in node.output])
#         if not in_graph:
#             # log(
#             #     f"Remove a floating node: {node.name}, the node output is: {node.output}"
#             # )
#             del_nodes.append(inode)

#     for i, init in enumerate(model.graph.initializer):
#         in_graph = init.name in in_graph_tensors
#         if not in_graph:
#             # log(f"Remove a unused initializer: {init.name}")
#             del_inits.append(i)

#     remove_node_and_init_by_indices(model.graph, del_nodes, del_inits, [])


def get_extractor(m: Union[onnx.ModelProto, onnx.GraphProto]):
    """Custom Extractor constructor to work with models >2GB which the default
    Extractor doesn't work with because infer_shapes doesn't work for it. This
    assumes that you've called infer_shapes_path() already on the model
    Args:
        m (onnx.ModelProto): Model to use for extractor
    Returns:
        onnx.utils.Extractor: Extractor
    """
    extractor = onnx.utils.Extractor(onnx.ModelProto())
    if isinstance(m, onnx.ModelProto):
        extractor.model = m
        # this is for compatibility with original Extractor
        extractor.graph = m.graph
    else:
        extractor.model = None
        extractor.graph = m
    extractor.wmap = extractor._build_name2obj_dict(extractor.graph.initializer)
    extractor.vimap = extractor._build_name2obj_dict(extractor.graph.value_info)

    extractor.wmap_loaded = set()
    return extractor


def load_model(
    path: Union[Path, str], load_external_data, infer_shapes=True
) -> onnx.ModelProto:
    if isinstance(path, str):
        path = Path(path)
    if infer_shapes:
        # this is needed explicitly to work for models > 2GB
        onnx.shape_inference.infer_shapes_path(path)
    model = onnx.load_model(path, load_external_data=load_external_data)

    if not load_external_data:
        model.metadata_props.add(key="onnx_utils_load", value=str(path.parent))
    return model


def load_extractor(path: Union[Path, str], load_external_data, infer_shapes=True):
    if isinstance(path, str):
        path = Path(path)
    model = load_model(path, load_external_data, infer_shapes)
    return get_extractor(model)


class Matcher:
    def __init__(self, pattern, quiet=False):
        self.lexer = Lexer(pattern)
        self.quiet = quiet

    def _match_io(self, input_params, input_names, variables):
        for item in input_params:
            if item != "?" and variables[item] not in input_names:
                return False
        return True

    # TODO(varunsh): add more documentation
    def _try_to_match(self, model, anchor, pattern_index=None, matched_pattern=None):
        """This is an updated matching function to replace the original one that
        was present. The original matching function only considered a depth
        based pattern where all nodes had to be children of the previous nodes.

        This pattern matcher allows matching on general patterns.
        """
        if matched_pattern is None:
            matched_pattern = [None] * len(self.lexer.patterns)

        if len(matched_pattern) == 1 and self.lexer.op_in_pattern(anchor.op_type):
            return [anchor]

        if not self.lexer.op_in_pattern(anchor.op_type):
            return matched_pattern

        if None not in matched_pattern:
            return matched_pattern

        if anchor in matched_pattern:
            return matched_pattern

        if pattern_index is not None:
            patterns = self.lexer.get_pattern_by_index(pattern_index)
        else:
            patterns = self.lexer.get_patterns_by_name(anchor.op_type)
        assert patterns

        for pattern, pattern_index in patterns:
            if matched_pattern[pattern_index] is not None:
                continue

            named_inputs, named_outputs = self.lexer.get_named_io(pattern)

            for io in named_inputs:
                edges = self.lexer.edges[io]
                # assert len(edges["src"]) == 1
                dsts = edges["dst"]
                srcs = edges["src"]
                assert len(srcs) == 1
                for dst in dsts:
                    io_index = dst["io_index"]
                    src_nodes = []
                    if len(anchor.input) > io_index:
                        src_nodes = find_nodes_by_output(
                            anchor.input[io_index], model.graph
                        )

                    for item in src_nodes:
                        if (
                            srcs[0]["name"] == item.op_type
                            and item.output[srcs[0]["io_index"]]
                            == anchor.input[io_index]
                        ):
                            matched_pattern[pattern_index] = anchor
                            if item not in matched_pattern:
                                matched_pattern = self._try_to_match(
                                    model,
                                    item,
                                    srcs[0]["pattern_index"],
                                    matched_pattern,
                                )
            for io in named_outputs:
                edges = self.lexer.edges[io]
                dsts = edges["dst"]
                srcs = edges["src"]
                assert len(srcs) == 1
                io_index = srcs[0]["io_index"]
                dst_nodes = []
                if len(anchor.output) > io_index:
                    dst_nodes = find_nodes_by_input(
                        anchor.output[io_index], model.graph
                    )
                for item in dst_nodes:
                    for dst in dsts:
                        if (
                            dst["name"] == item.op_type
                            and item.input[dst["io_index"]] == anchor.output[io_index]
                        ):
                            matched_pattern[pattern_index] = anchor
                            if item not in matched_pattern:
                                matched_pattern = self._try_to_match(
                                    model, item, dst["pattern_index"], matched_pattern
                                )

        return matched_pattern

    def match(self, model):
        all_matched_pairs = []
        all_matched_set = set()
        for index, node in enumerate(model.graph.node):
            if node.op_type in {"Scan", "Loop"}:
                subgraph = onnx.helper.get_node_attr_value(node, "body")
                sub_model = onnx.helper.make_model(
                    subgraph, producer_name="from_subgraph"
                )
                all_matched_pairs.extend(self.match(sub_model))
            elif node.op_type == "If":
                then_branch = onnx.helper.get_node_attr_value(node, "then_branch")
                then_branch_sub_model = onnx.helper.make_model(
                    then_branch, producer_name="from_then_branch"
                )
                all_matched_pairs.extend(self.match(then_branch_sub_model))
                else_branch = onnx.helper.get_node_attr_value(node, "else_branch")
                else_branch_sub_model = onnx.helper.make_model(
                    else_branch, producer_name="from_else_branch"
                )
                all_matched_pairs.extend(self.match(else_branch_sub_model))
            else:
                if node.op_type == "Constant":
                    continue
                # since the matcher can now use any node as the anchor, reduce
                # the search space by the op determined to be the best anchor
                if self.lexer.anchor != "?" and node.op_type != self.lexer.anchor:
                    continue
                potential_match = self._try_to_match(model, node)  # match
                if None in potential_match:
                    continue
                if not node.name:
                    node.name = node.op_type + f"_{index}"
                node_names = ",".join([node.name for node in potential_match])
                if node_names not in all_matched_set:
                    all_matched_set.add(node_names)
                    if (potential_match) not in all_matched_pairs:
                        all_matched_pairs.append(potential_match)
        return all_matched_pairs

    def print_match(self, model):
        print("=====================================================================")
        matched_subgraphs = self.match(model)
        log(f"Found {len(matched_subgraphs)} subgraphs:")
        for i, subgraph in enumerate(self.match(model)):
            subgraph_names = ", ".join(
                [f"{item.name}({item.op_type})" for item in subgraph]
            )
            print(f"\tSubgraph{i}: {subgraph_names}")

        pattern_text = "\n\t".join(self.lexer.lines)
        log(f"Pattern is:\n\t{pattern_text}")
        print("=====================================================================")

    # replace some subgraph to new
    def replace(
        self,
        extractor: onnx.utils.Extractor,
        new_graph_fn,
        pass_id: str,
        params: ReplaceParams,
        max_to_replace=None,
    ):
        matched_subgraphs = self.match(extractor.model)
        # -1 means this is a global pass so no pattern is used and no replacements made
        replacement_count = (
            -1
            if matched_subgraphs and all(not elem for elem in matched_subgraphs)
            else 0
        )

        if max_to_replace is not None and max_to_replace < len(matched_subgraphs):
            print(f"Reducing {len(matched_subgraphs)} to first {max_to_replace}")
            matched_subgraphs = matched_subgraphs[:max_to_replace]

        # resolve main graph
        for i, subgraph in enumerate(matched_subgraphs):
            if not all([node in extractor.graph.node for node in subgraph]):
                continue
            rewrite_nodes = True
            if new_graph_fn is not None:
                new_nodes, new_initializers, new_tvis = new_graph_fn(
                    extractor, f"{pass_id}_{i}", copy.deepcopy(subgraph), params
                )
            else:
                new_nodes, new_initializers = [], []

            if new_nodes is None:
                rewrite_nodes = False
                new_nodes = []

            if subgraph != new_nodes:
                assert replacement_count >= 0
                replacement_count += 1

            new_graph_names = ", ".join(
                [f"{item.name}({item.op_type})" for item in new_nodes]
            )
            subgraph_names = ", ".join(
                [f"{item.name}({item.op_type})" for item in subgraph]
            )
            if not self.quiet:
                if len(new_nodes) > 0:
                    log(
                        f"Replace subgraph{i}: [{subgraph_names}] to: [{new_graph_names}]"
                    )
                else:
                    log(f"Delete subgraph{i}: {subgraph_names}")

            nodes_list = list(extractor.graph.node)
            indices = sorted(
                [nodes_list.index(item) for item in subgraph], reverse=True
            )

            for i in indices:
                del extractor.graph.node[i]

            if len(new_nodes) == 0 and rewrite_nodes:
                input_node = subgraph[0]
                output_node = subgraph[-1]
                assert (
                    len(input_node.input) == len(output_node.output)
                    and new_graph_fn is None
                    or new_graph_fn is not None
                ), "Invalid replace"
                # rewrite the child nodes of the replaced block to use the new input
                # from before the replaced block.
                o2i = {a: b for a, b in zip(output_node.output, input_node.input)}
                for output_name in output_node.output:
                    if is_output_edge(output_name, extractor.graph):
                        # However, this doesn't work if the replaced block is at
                        # the end of the graph (no child nodes), so rewrite parents
                        # instead
                        input_name = o2i[output_name]
                        parents = find_nodes_by_output(input_name, extractor.graph)
                        for p in parents:
                            p.output[list(p.output).index(input_name)] = output_name
                    else:
                        children = find_nodes_by_input(output_name, extractor.graph)
                        for c in children:
                            c.input[list(c.input).index(output_name)] = o2i[output_name]
            elif indices:
                insert_point = indices[-1]
                for node in new_nodes:
                    extractor.graph.node.insert(insert_point, node)
                    insert_point += 1
            else:
                # this should be a global pass in this case
                assert replacement_count == -1

            # disable this in the interest of runtime
            # for n in subgraph:
            #     # Remove the node and its corresponding information if it is not in new_nodes
            #     remove_node_and_info(extractor, n)

            if new_tvis:
                for tvi in new_tvis:
                    if tvi.name in extractor.vimap:
                        idx = -1
                        for index, tvi_2 in enumerate(extractor.graph.value_info):
                            if tvi_2.name == tvi.name:
                                idx = index
                                break
                        assert idx != -1
                        del extractor.graph.value_info[idx]
                    extractor.graph.value_info.append(tvi)
                    extractor.vimap[tvi.name] = tvi

            for init in new_initializers:
                # don't maintain this in the interim and set it at the end
                # extractor.graph.initializer.append(init)
                extractor.wmap[init.name] = init

        # resolve subgraph(s) if any
        subgraph_nodes = [
            node
            for node in extractor.graph.node
            if node.op_type in {"Scan", "Loop", "If"}
        ]
        for subgraph_node in subgraph_nodes:
            if subgraph_node.op_type in {"Scan", "Loop"}:
                sub_graph = onnx.helper.get_node_attr_value(subgraph_node, "body")
                sub_model = onnx.helper.make_model(
                    sub_graph, producer_name="from_subgraph"
                )
                sub_extractor = get_extractor(sub_model)
                replacement_count += self.replace(
                    sub_extractor, new_graph_fn, pass_id, params, max_to_replace
                )
            elif node.op_type == "If":
                then_branch = onnx.helper.get_node_attr_value(node, "then_branch")
                then_branch_sub_model = onnx.helper.make_model(
                    then_branch, producer_name="from_then_branch"
                )
                sub_extractor = get_extractor(then_branch_sub_model)
                replacement_count += self.replace(
                    sub_extractor, new_graph_fn, pass_id, params, max_to_replace
                )
                else_branch = onnx.helper.get_node_attr_value(node, "else_branch")
                else_branch_sub_model = onnx.helper.make_model(
                    else_branch, producer_name="from_else_branch"
                )
                sub_extractor = get_extractor(else_branch_sub_model)
                replacement_count += self.replace(
                    sub_extractor, new_graph_fn, pass_id, params, max_to_replace
                )

        return replacement_count
