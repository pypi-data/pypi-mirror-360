# Copyright (c) 2024 Advanced Micro Devices, Inc.

import importlib
import os
import shutil
import sys
from pathlib import Path
from typing import Optional

import onnx
import onnx.external_data_helper
import sympy
from onnxruntime.tools.onnx_model_utils import (
    make_dim_param_fixed,
)
from onnxruntime.tools.symbolic_shape_infer import SymbolicShapeInference

import ryzenai_onnx_utils.matcher
import ryzenai_onnx_utils.partitioner
import ryzenai_onnx_utils.utils


def configure_parser(subparser):
    preprocess_parser = subparser.add_parser("preprocess")
    preprocess_parser.add_argument(
        "input_path", type=Path, help="Path to input ONNX model"
    )
    preprocess_parser.add_argument(
        "output_path", type=Path, help="Path to output ONNX model"
    )
    preprocess_parser.add_argument(
        "--optimize",
        type=Path,
        help="Run an optimize script",
    )
    preprocess_parser.add_argument(
        "--keep-dynamic",
        action="store_true",
        help="Skip fixing the input shapes to preserve dynamic input shapes",
    )
    preprocess_parser.add_argument(
        "--save-as-external",
        action="store_true",
        help="Save the model with external data",
    )
    preprocess_parser.add_argument(
        "--size-threshold",
        type=int,
        default=1024,  # default value for onnx.save_model()
        help="Threshold of the buffer to move to external data. Does nothing if --save-as-external is not specified",
    )

    return preprocess_parser


# def fix_output_shapes(model_path: str):
#     """
#     Update the output shapesof a model where the input shape/s were made fixed, if possible.
#     This is mainly to make the model usage clearer if the output shapes can be inferred from the new input shapes.
#     :param model: Model that had input shapes fixed.
#     """

#     # get a version of the model with shape inferencing info in it. this will provide fixed output shapes if possible.
#     model = onnx.load_model(model_path)

#     for idx, o in enumerate(model.graph.output):
#         if not is_fixed_size_tensor(o):
#             new_o = m2.graph.output[idx]
#             if is_fixed_size_tensor(new_o):
#                 o.type.tensor_type.shape.CopyFrom(new_o.type.tensor_type.shape)

#     return m2


def get_input_tvis(original_graph: onnx.GraphProto, input_map, index: int):
    new_tvis = []
    for tvi in original_graph.input:
        old_shape = ryzenai_onnx_utils.matcher.get_shape(tvi)
        new_shape = []
        for i in old_shape:
            if i in input_map:
                new_shape.append(input_map[i][index])
            else:
                new_shape.append(i)
        new_tvis.append(
            onnx.helper.make_tensor_value_info(
                tvi.name, tvi.type.tensor_type.elem_type, new_shape
            )
        )
    return new_tvis


def rename_edge(graph: onnx.GraphProto, old_name: str, new_name: str):
    for i, node in enumerate(graph.node):
        for j, input_name in enumerate(node.input):
            if input_name == old_name:
                graph.node[i].input[j] = new_name
        for j, output_name in enumerate(node.output):
            if output_name == old_name:
                graph.node[i].output[j] = new_name

    for i, input_tvi in enumerate(graph.input):
        if input_tvi.name == old_name:
            graph.input[i].name = new_name
    for i, output_tvi in enumerate(graph.output):
        if output_tvi.name == old_name:
            graph.output[i].name = new_name


def recurse_add_ifs(
    original_graph: onnx.GraphProto,
    input_map,
    input_combos: list[list[int]],
    index: int,
    graphs: list[onnx.GraphProto],
    add_fallback: bool,
):
    new_nodes = []
    # index = 0
    new_nodes.append(
        onnx.helper.make_node(
            "Constant",
            inputs=[],
            outputs=[f"comparison_{index}"],
            value_ints=input_combos[0],
            name=f"const_{index}",
        )
    )
    new_nodes.append(
        onnx.helper.make_node(
            "Equal",
            inputs=["shape_concat", f"comparison_{index}"],
            outputs=[f"cond_{index}"],
            name=f"equal_{index}",
        )
    )
    new_nodes.append(
        onnx.helper.make_node(
            "ReduceMin",
            inputs=[f"cond_{index}"],
            outputs=[f"reduced_cond_{index}"],
            name=f"reduce_min_{index}",
            keepdims=0,
        )
    )
    value_info_0 = graphs[0].value_info
    new_tvis = get_input_tvis(original_graph, input_map, index)
    value_info_0.extend(new_tvis)
    for output_tvi in original_graph.output:
        rename_edge(graphs[0], output_tvi.name, f"{output_tvi.name}_{index}")
    # TODO(varunsh): assuming add_fallback is false!
    if len(input_combos) == 2:
        value_info_1 = graphs[1].value_info
        new_tvis = get_input_tvis(original_graph, input_map, index + 1)
        value_info_1.extend(new_tvis)
        for output_tvi in original_graph.output:
            rename_edge(graphs[1], output_tvi.name, f"{output_tvi.name}_{index+1}")

        output_names = (
            [x.name for x in original_graph.output]
            if index == 0
            else [f"{x.name}_if_{index}" for x in original_graph.output]
        )
        # value_info_0.extend(original_graph.input)
        new_nodes.append(
            onnx.helper.make_node(
                "If",
                inputs=[f"reduced_cond_{index}"],
                outputs=output_names,
                name=f"if_{index}",
                then_branch=onnx.helper.make_graph(
                    graphs[0].node,
                    f"{original_graph.name}_{index}",
                    [],
                    graphs[0].output,
                    graphs[0].initializer,
                    value_info=value_info_0,
                ),
                else_branch=onnx.helper.make_graph(
                    graphs[1].node,
                    f"{original_graph.name}_{index+1}",
                    [],
                    graphs[1].output,
                    graphs[1].initializer,
                    value_info=value_info_1,
                ),
            )
        )
    else:
        sub_nodes = recurse_add_ifs(
            original_graph,
            input_map,
            input_combos[1:],
            index + 1,
            graphs[1:],
            add_fallback,
        )
        graph = onnx.helper.make_graph(
            sub_nodes, f"else_{index}", [], original_graph.output
        )
        for output_tvi in original_graph.output:
            rename_edge(graph, output_tvi.name, f"{output_tvi.name}_if_{index+1}")
        output_names = (
            [x.name for x in original_graph.output]
            if index == 0
            else [f"{x.name}_if_{index}" for x in original_graph.output]
        )
        new_nodes.append(
            onnx.helper.make_node(
                "If",
                inputs=[f"reduced_cond_{index}"],
                outputs=output_names,
                name=f"if_{index}",
                then_branch=onnx.helper.make_graph(
                    graphs[0].node,
                    f"{original_graph.name}_{index}",
                    [],
                    graphs[0].output,
                    graphs[0].initializer,
                    value_info=value_info_0,
                ),
                else_branch=graph,
            )
        )
    return new_nodes


def add_ifs(
    original_graph: onnx.GraphProto,
    graphs: list[onnx.GraphProto],
    input_map: dict[str, list],
    multiple_shapes: list[tuple[str, int]],
    add_fallback: bool,
):
    input_combos = list(zip(*input_map.values()))
    # without a fallback, the last combination is the final else case
    # if not add_fallback:
    #     input_combos.pop()

    new_nodes = []
    shape_outputs = []
    for index, value in enumerate(multiple_shapes):
        input_name, input_index = value
        shape_outputs.append(f"shape_{index}")
        new_nodes.append(
            onnx.helper.make_node(
                "Shape",
                inputs=[input_name],
                outputs=[shape_outputs[-1]],
                name=f"input_shape_{index}",
                start=input_index,
                end=input_index + 1,
            )
        )

    new_nodes.append(
        onnx.helper.make_node(
            "Concat",
            inputs=shape_outputs,
            outputs=["shape_concat"],
            name="input_shape_concat",
            axis=0,
        )
    )
    input_shape_concat_tvi = onnx.helper.make_tensor_value_info(
        "shape_concat", onnx.TensorProto.INT64, [len(shape_outputs)]
    )
    input_tvis = list(original_graph.input)

    new_nodes.extend(
        recurse_add_ifs(
            original_graph, input_map, input_combos, 0, graphs, add_fallback
        )
    )
    graph = onnx.helper.make_graph(
        new_nodes,
        "else_0",
        input_tvis,
        original_graph.output,
        value_info=[input_shape_concat_tvi],
    )
    model = onnx.helper.make_model(graph)
    opset = model.opset_import.add()
    opset.domain = "com.microsoft"
    opset.version = 23

    return model


def parse_user_val_int(user_val: str):
    try:
        return int(user_val)
    except ValueError:
        print(f"{user_val} cannot be converted to an integer")
    return None


def parse_user_val_int_or_list(user_val: str):
    if "," not in user_val:
        try:
            return [int(user_val)]
        except ValueError:
            return [user_val]
    user_vals = user_val.split(",")
    new_vals = []
    for val in user_vals:
        try:
            new_vals.append(int(val))
        except ValueError:
            new_vals.append(val)
    return new_vals


def prompt_for_dim(elem: str, validator_func):
    user_vals = None
    while user_vals is None:
        user_val = input(f"Enter fixed value(s) for {elem}: ")
        user_vals = validator_func(user_val)
    return user_vals


def check_dynamic_inputs(extractor: onnx.utils.Extractor):
    input_map = {}
    has_dynamic_inputs = False
    multiple_shapes = []
    num_graphs = prompt_for_dim("graphs", parse_user_val_int)
    # num_graphs = 4
    graphs = []
    for _ in range(num_graphs):
        new_graph = onnx.GraphProto()
        new_graph.CopyFrom(extractor.model.graph)
        graphs.append(new_graph)

    for input_tvi in extractor.model.graph.input:
        shape = ryzenai_onnx_utils.matcher.get_shape(input_tvi)
        for index, elem in enumerate(shape):
            if isinstance(elem, str):
                valid = False
                while not valid:
                    values = (
                        prompt_for_dim(elem, parse_user_val_int_or_list)
                        if elem not in input_map
                        else input_map[elem]
                    )
                    if len(values) == num_graphs:
                        valid = True
                    else:
                        print(
                            f"Number of dimensions ({len(values)}) must match number of graphs ({num_graphs})"
                        )
                if len(values) > 1:
                    multiple_shapes.append((input_tvi.name, index))
                for index_2, value in enumerate(values):
                    if not isinstance(value, int):
                        continue
                    make_dim_param_fixed(graphs[index_2], elem, value)
                input_map[elem] = values
                has_dynamic_inputs = True
    # if num_graphs > 1:
    #     # TODO(varunsh): add_fallback hardcoded to False for now
    #     new_model = add_ifs(extractor.model.graph, input_map, multiple_shapes, False)
    #     extractor = ryzenai_onnx_utils.matcher.get_extractor(new_model)
    return graphs, has_dynamic_inputs, input_map, multiple_shapes


def fix_input_output_shapes(
    extractor, output_path: Path, save_as_external, external_data_extension
):
    graphs, has_dynamic_inputs, input_map, multiple_shapes = check_dynamic_inputs(
        extractor
    )
    stem = output_path.stem
    for index, graph in enumerate(graphs):
        local_output_path = output_path.parent / (stem + f"_{index}.onnx")
        location = f"{stem}_{index}.{external_data_extension}"
        opsets = [
            onnx.OperatorSetIdProto(domain="ai.onnx", version=14),
            onnx.OperatorSetIdProto(domain="com.microsoft", version=1),
        ]
        model = onnx.helper.make_model(graph, opset_imports=opsets)
        onnx.save_model(
            model,
            local_output_path,
            save_as_external_data=save_as_external,
            location=location,
        )
        if has_dynamic_inputs:
            # TODO(varunsh): do we need to do this at all?
            # new_model = fix_output_shapes(output_path)
            onnx.shape_inference.infer_shapes_path(local_output_path)
    return len(graphs), input_map, multiple_shapes


def optimize_model(
    model_preprocessing: Path,
    input_path: Path,
    output_path: Path,
    save_as_external: bool,
    size_threshold: int,
    external_data_extension: str,
):
    if model_preprocessing.is_absolute():
        optimizer = ryzenai_onnx_utils.utils.load_module_from_file(
            model_preprocessing, "optimizer"
        )
    else:
        optimizer = importlib.import_module(
            f"ryzenai_onnx_utils.model_preprocessing.{model_preprocessing}"
        )
    if hasattr(optimizer, "pre_optimize_passes"):
        ryzenai_onnx_utils.partitioner._run_manual_passes(
            input_path,
            input_path,
            save_as_external,
            f"{input_path.stem}.{external_data_extension}",
            optimizer.pre_optimize_passes(),
        )
    optimizer.optimize(
        input_path,
        output_path,
        save_as_external,
        size_threshold,
        external_data_extension,
    )


def all_io_inferred(node: onnx.NodeProto, extractor, io_type: str):
    assert io_type in ["input", "output"]
    is_output = io_type == "output"
    io = getattr(node, io_type)
    for name in io:
        if not name:
            continue
        if (name not in extractor.vimap) and (name not in extractor.wmap):
            return False
        if (
            name in extractor.vimap
            and not ryzenai_onnx_utils.matcher.is_initializer(name, extractor)
            and not check_tensor_shape_dims(extractor.vimap[name], is_output)
        ):
            return False
    return True


def all_inputs_inferred(node: onnx.NodeProto, extractor):
    return all_io_inferred(node, extractor, "input")


def all_outputs_inferred(node: onnx.NodeProto, extractor):
    return all_io_inferred(node, extractor, "output")


def infer_outputs(node: onnx.NodeProto, extractor):
    op_type = node.op_type
    try:
        inferrer = importlib.import_module(
            f"ryzenai_onnx_utils.shape_inference.{op_type}"
        )
        inferrer.infer_outputs(node, extractor)
    except ModuleNotFoundError:
        print(f"No shape inference script found for {op_type}: {node.name}")
        sys.exit(1)


def _infer_shapes(
    wavefront: list, extractor: onnx.utils.Extractor, output_set: set, input_map: dict
):
    iterations = 0
    infinite_loop_condition = 10000
    processed_nodes = set()
    while wavefront:
        iterations += 1
        edge = wavefront.pop(0)
        if edge in output_set:
            continue
        if edge not in input_map:
            continue
        nodes_indices = input_map[edge]
        nodes = [extractor.graph.node[i] for i in nodes_indices]
        for node in nodes:
            if node.name in processed_nodes:
                continue
            if all_inputs_inferred(node, extractor) or all_outputs_inferred(
                node, extractor
            ):
                if not all_outputs_inferred(node, extractor):
                    infer_outputs(node, extractor)
                processed_nodes.add(node.name)
                wavefront.extend(node.output)
            else:
                if edge not in wavefront:
                    wavefront.append(edge)
                break
        if iterations > infinite_loop_condition:
            raise ValueError("Possible infinite loop when trying to infer shapes")


def do_infer_shapes(
    extractor: onnx.utils.Extractor, inputs: Optional[list[str]] = None
):
    graph = extractor.graph

    # only the top-level graph has inputs
    original_inputs = [i.name for i in graph.input] if graph.input else inputs

    input_map = ryzenai_onnx_utils.matcher.build_input_map(extractor)
    has_nested_if = False
    for node in graph.node:
        if node.op_type == "If":
            then_branch = onnx.helper.get_node_attr_value(node, "then_branch")
            extractor_0 = ryzenai_onnx_utils.matcher.get_extractor(then_branch)
            graph_0 = do_infer_shapes(extractor_0, original_inputs)
            else_branch = onnx.helper.get_node_attr_value(node, "else_branch")
            extractor_1 = ryzenai_onnx_utils.matcher.get_extractor(else_branch)
            graph_1 = do_infer_shapes(extractor_1, original_inputs)
            ryzenai_onnx_utils.matcher.set_attribute(node, "then_branch", graph_0)
            ryzenai_onnx_utils.matcher.set_attribute(node, "else_branch", graph_1)
            has_nested_if = True

    if graph.input and has_nested_if:
        # top-level graph with an if. Don't infer shapes here
        return graph
    else:
        if all(x in input_map for x in original_inputs):
            # leaf of the if-then tree with the real graph
            wavefront = [x for x in original_inputs]
        else:
            # intermediate if-then without the real graph
            return graph

    for tvi in graph.input:
        extractor.vimap[tvi.name] = tvi
    output_set = set()
    for tvi in graph.output:
        extractor.vimap[tvi.name] = tvi
        output_set.add(tvi.name)

    _infer_shapes(wavefront, extractor, output_set, input_map)

    del graph.value_info[:]
    for _, tvi in extractor.vimap.items():
        graph.value_info.append(tvi)

    return graph


def rename_external_location(graph: onnx.GraphProto, new_location, old_location=None):
    for index, init in enumerate(graph.initializer):
        if onnx.external_data_helper.uses_external_data(init):
            external_data = {}
            for ext in graph.initializer[index].external_data:
                external_data[ext.key] = ext.value
            # assuming only one location for all tensors
            old_location = external_data["location"]
            external_data["location"] = new_location
            ryzenai_onnx_utils.matcher.set_external_data(
                graph.initializer[index], **external_data
            )
    for index, node in enumerate(graph.node):
        if node.op_type == "If":
            else_graph = onnx.helper.get_node_attr_value(node, "else_branch")
            old_location = rename_external_location(
                else_graph, new_location, old_location
            )
            ryzenai_onnx_utils.matcher.set_attribute(
                graph.node[index], "else_branch", else_graph
            )
            then_graph = onnx.helper.get_node_attr_value(node, "then_branch")
            old_location = rename_external_location(
                then_graph, new_location, old_location
            )
            ryzenai_onnx_utils.matcher.set_attribute(
                graph.node[index], "then_branch", then_graph
            )
        elif node.op_type == "Loop" or node.op_type == "Scan":
            loop_graph = onnx.helper.get_node_attr_value(node, "body")
            old_location = rename_external_location(
                loop_graph, new_location, old_location
            )
            ryzenai_onnx_utils.matcher.set_attribute(
                graph.node[index], "body", loop_graph
            )
    return old_location


def is_dim_integer(dim):
    return dim.HasField("dim_value")


def check_tensor_shape_dims(tensor, is_output):
    """
    Check if a tensor's shape dimensions are all inferred as integers. There are
    a few corner cases:

    A tensor's dim may be empty. For output tensors, this means it's undefined
    and needs to be inferred. However, an input integer tensor will also have an
    undefined shape but that should be noted as already inferred. The first
    check on if the shape's dim exists is meant to address this: if it's an
    input tensor with undefined inputs, maybe that's fine.

    There is a difference between a TensorProto has a shape {} and no shape.
    The former means that it maybe a scalar_tensor. The latter means that it has
    no shape.

    Args:
        tensor (onnx.TensorProto): The tensor to examine
        is_output (bool): True if the tensor is an output tensor.

    Returns:
        bool: Returns true if all shape dimensions are already integers.
    """
    if not tensor.type.tensor_type.HasField("shape"):
        return False
    if is_output and len(tensor.type.tensor_type.shape.dim) == 0:
        return False
    for dim in tensor.type.tensor_type.shape.dim:
        if is_dim_integer(dim):
            continue
        else:
            return False
    return True


def has_dynamic_inputs(graph: onnx.GraphProto):
    return not all([check_tensor_shape_dims(i, False) for i in graph.input])


def check_shape(model):
    constant_names = {initializer.name for initializer in model.graph.initializer}

    def find_nodes_with_tensors_without_shape(model):
        nodes_with_missing_shape_tensors = []
        for node in model.graph.node:
            for output in node.output:
                tensor_info = next(
                    (vi for vi in model.graph.value_info if vi.name == output), None
                )
                if (
                    not check_tensor_shape_dims(tensor_info, True)
                    and output not in constant_names
                ) or (
                    tensor_info
                    and not tensor_info.type.tensor_type.shape.dim
                    and output not in constant_names
                ):
                    nodes_with_missing_shape_tensors.append(
                        (node.name, node.op_type, output)
                    )
        return nodes_with_missing_shape_tensors

    nodes_with_missing_shape_tensors = find_nodes_with_tensors_without_shape(model)

    if nodes_with_missing_shape_tensors:
        print(f"there are {len(nodes_with_missing_shape_tensors)} tensors miss shape")
        print("The following tensors miss shape, generated by node:")
        for node_name, op_type, tensor_name in nodes_with_missing_shape_tensors:
            print(f"node: {node_name} (op type: {op_type}) tensor: {tensor_name}")
    else:
        print("All tensors have shape information or constant")


def infer_shapes(
    input_path: Path,
    output_path: Path,
    save_as_external: bool,
    old_external_location: str,
    external_data_extension: str,
):
    extractor = ryzenai_onnx_utils.matcher.load_extractor(input_path, False)

    # the location is only used if save_as_external is True
    stem = output_path.stem
    location = f"{stem}.{external_data_extension}"
    if save_as_external:
        # delete existing data if it exists
        output_path.with_suffix(f".{external_data_extension}").unlink(True)
        rename_external_location(extractor.model.graph, location)
        if Path.exists(input_path.parent / old_external_location):
            os.rename(
                input_path.parent / old_external_location, output_path.parent / location
            )

    try:
        graph = do_infer_shapes(extractor)
    except SystemExit:
        print("shape infer failed, continue.")
        graph = extractor.graph
    except ValueError:
        print("shape infer infinite loop, continue.")
        graph = extractor.graph
    opsets = [
        onnx.OperatorSetIdProto(domain="ai.onnx", version=14),
        onnx.OperatorSetIdProto(domain="com.microsoft", version=1),
    ]
    model = onnx.helper.make_model(graph, opset_imports=opsets)
    onnx.save_model(
        model,
        output_path,
        save_as_external_data=save_as_external,
        location=location,
    )


def complete_node_names(input_path, output_path):
    model = onnx.load_model(input_path, load_external_data=False)
    name_set = set()
    for node in model.graph.node:
        if node.name:
            if node.name not in name_set:
                name_set.add(node.name)
            else:
                # this shouldn't happen but it's a check for safety
                raise ValueError(f"Duplicate node name detected: {node.name}")

    type_idx_map = {}
    for node in model.graph.node:
        if not node.name:
            idx = 0
            if node.op_type not in type_idx_map:
                type_idx_map[node.op_type] = 0
            else:
                type_idx_map[node.op_type] += 1
                idx = type_idx_map[node.op_type]
            # check
            new_name = f"{node.op_type}_{idx}"
            while new_name in name_set:
                new_name = f"{node.op_type}_{idx + 1}"
                type_idx_map[node.op_type] += 1
            node.name = new_name
            name_set.add(new_name)
    onnx.save_model(model, output_path)


def collect_dim_params_from_tensor_type(tensor_type) -> set[str]:
    dim_params = set()
    if tensor_type.HasField("shape"):
        for dim in tensor_type.shape.dim:
            if dim.HasField("dim_param") and dim.dim_param:
                dim_params.add(dim.dim_param.strip())
    return dim_params


def extract_all_dim_params_from_onnx(model: onnx.ModelProto) -> set[str]:
    dim_params = set()

    def process_value_info(value_info_list):
        for value_info in value_info_list:
            if value_info.type.HasField("tensor_type"):
                dim_params.update(
                    collect_dim_params_from_tensor_type(value_info.type.tensor_type)
                )

    graph = model.graph
    process_value_info(graph.input)
    process_value_info(graph.output)
    process_value_info(graph.value_info)
    # if hasattr(graph, "sparse_initializer"):
    #     process_value_info(graph.sparse_initializer)

    return dim_params


def extract_symbol_table_from_inputs(model: onnx.ModelProto) -> set[str]:
    symbol_table = set()
    for value_info in model.graph.input:
        if value_info.type.HasField("tensor_type"):
            symbol_table.update(
                collect_dim_params_from_tensor_type(value_info.type.tensor_type)
            )
    return symbol_table


def can_expr_be_resolved(expr: str, symbol_table: set[str]) -> bool:
    expr = expr.strip()
    try:
        parsed = sympy.sympify(expr, evaluate=False)
        used_symbols = {str(s) for s in parsed.free_symbols}
        return used_symbols <= symbol_table
    except Exception:
        return False


def infer_symbolic_shapes(model: onnx.ModelProto):
    # huisu: SymbolicShapeInference has bugs with nhwcconv with fixed shapes
    # cannot replace the existing shape inference with SymbolicShapeInference
    if not has_dynamic_inputs(model.graph):
        return model
    return SymbolicShapeInference.infer_shapes(model, auto_merge=True, verbose=1)


def check_symbolic_completeness(model: onnx.ModelProto):
    symbol_table = extract_symbol_table_from_inputs(model)
    dim_params = extract_all_dim_params_from_onnx(model)
    missing = {dp for dp in dim_params if not can_expr_be_resolved(dp, symbol_table)}
    return missing


def dynamic_shape_infer(input_path, output_path, save_as_external, location):
    model = onnx.load_model(input_path, load_external_data=False)
    inputs_static = not has_dynamic_inputs(model.graph)
    if inputs_static or not check_symbolic_completeness(model):
        # No need to re-infer symbolic shapes
        if input_path != output_path:
            onnx.save_model(
                model,
                output_path,
                save_as_external_data=save_as_external,
                location=location,
            )
        else:
            if inputs_static:
                print("fixed graph input shape, skip dynamic_shape_infer")
            else:
                print(
                    "Symbolic shape completeness check is passed, skip dynamic_shape_infer"
                )
    else:
        print("Reinferring dynamic shape...")
        for output in model.graph.output:
            tensor_type = output.type.tensor_type
            if tensor_type.HasField("shape"):
                tensor_type.ClearField("shape")
        for value_info in model.graph.value_info:
            tensor_type = value_info.type.tensor_type
            if tensor_type.HasField("shape"):
                tensor_type.ClearField("shape")
        symbolic_model = infer_symbolic_shapes(model)
        onnx.save_model(
            symbolic_model,
            output_path,
            save_as_external_data=save_as_external,
            location=location,
        )
        print("Reinferred dynamic shape...")
        missing = check_symbolic_completeness(symbolic_model)
        if missing:
            print(
                f"Symbolic shape inference is incomplete. "
                f"The following symbolic dimensions are missing from the symbol table: {missing}"
            )


def main(args):
    save_as_external = args.save_as_external

    if save_as_external:
        tmp_model_0 = args.input_path.parent / "tmp_0.onnx"
        ryzenai_onnx_utils.matcher.convert_to_external(
            args.input_path, tmp_model_0, args.external_data_extension
        )
    else:
        tmp_model_0 = args.input_path

    extractor = ryzenai_onnx_utils.matcher.load_extractor(tmp_model_0, False)
    if not args.keep_dynamic:
        tmp_model = args.input_path.parent / "tmp_1.onnx"
        print("Fixing input and output shapes...")
        num_graphs, input_map, multiple_shapes = fix_input_output_shapes(
            extractor, tmp_model, save_as_external, args.external_data_extension
        )
        print("Fixed input and output shapes")
    else:
        tmp_model = tmp_model_0
        num_graphs = 1
        input_map = None
        multiple_shapes = None
    if args.optimize is not None:
        print("Optimizing model...")
        tmp_model_2 = args.input_path.parent / "tmp_2.onnx"
        for i in range(num_graphs):
            tmp_model_1 = tmp_model.parent / f"tmp_1_{i}.onnx"
            shutil.copy(tmp_model_1, tmp_model_2)
            optimize_model(
                args.optimize,
                tmp_model_2,
                tmp_model_1,
                save_as_external,
                args.size_threshold,
                args.external_data_extension,
            )
            ryzenai_onnx_utils.matcher.delete_model(
                tmp_model_2, args.external_data_extension
            )
        print("Optimized model")

    if num_graphs == 1:
        tmp_model = tmp_model.parent / "tmp_1_0.onnx"
        if args.optimize is None:
            tmp_model_1 = tmp_model
    else:
        # TODO(varunsh): currently, this path assumes optimization was done
        assert args.optimize is not None
        graphs = []
        for i in range(num_graphs):
            tmp_model_1 = tmp_model.parent / f"tmp_1_{i}.onnx"
            graphs.append(onnx.load_model(tmp_model_1, load_external_data=False).graph)
            # ryzenai_onnx_utils.matcher.delete_model(tmp_model_1)
        # TODO(varunsh): add_fallback hardcoded to False for now
        new_model = add_ifs(
            extractor.model.graph, graphs, input_map, multiple_shapes, False
        )
        stem = tmp_model.stem
        location = f"{stem}.{args.external_data_extension}"
        onnx.save_model(
            new_model,
            tmp_model,
            save_as_external_data=save_as_external,
            location=location,
        )
    print("Inferring shapes...")
    if args.optimize is None:
        tmp_model_1 = tmp_model_0
    infer_shapes(
        tmp_model,
        args.output_path,
        save_as_external,
        f"{tmp_model_1.stem}.{args.external_data_extension}",
        args.external_data_extension,
    )
    print("Inferred shapes")

    if tmp_model != args.input_path:
        ryzenai_onnx_utils.matcher.delete_model(tmp_model, args.external_data_extension)
    if save_as_external:
        ryzenai_onnx_utils.matcher.delete_model(
            tmp_model_0, args.external_data_extension
        )
    for i in range(num_graphs):
        tmp_model_1 = tmp_model.parent / f"tmp_1_{i}.onnx"
        ryzenai_onnx_utils.matcher.delete_model(
            tmp_model_1, args.external_data_extension
        )

    if args.optimize is not None:
        if args.optimize.is_absolute():
            optimizer = ryzenai_onnx_utils.utils.load_module_from_file(
                args.optimize, "optimizer"
            )
        else:
            optimizer = importlib.import_module(
                f"ryzenai_onnx_utils.model_preprocessing.{args.optimize}"
            )
        if hasattr(optimizer, "finalize"):
            ryzenai_onnx_utils.partitioner._run_manual_passes(
                args.output_path,
                args.output_path,
                save_as_external,
                f"{args.output_path.stem}.{args.external_data_extension}",
                optimizer.finalize(),
            )
    dynamic_shape_infer(
        args.output_path,
        args.output_path,
        args.save_as_external,
        f"{args.output_path.stem}.{args.external_data_extension}",
    )
    print("Adding missing node names...")
    complete_node_names(args.output_path, args.output_path)
    print("Added missing node names")
