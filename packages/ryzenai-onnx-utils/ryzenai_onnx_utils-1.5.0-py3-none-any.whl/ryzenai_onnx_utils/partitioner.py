# Copyright (c) 2024 Advanced Micro Devices, Inc.

import argparse
import copy
import functools
import importlib
import importlib.resources
import shutil
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Optional

import onnx
import yaml

import ryzenai_onnx_utils.matcher
import ryzenai_onnx_utils.utils
from ryzenai_onnx_utils.passes import SubPass

try:
    import ryzenai_onnx_utils.extract

    EXTRACT = True
except ImportError:
    EXTRACT = False

try:
    import ryzenai_onnx_utils.pattern_builder as pb
    import ryzenai_onnx_utils.pattern_generator as pg

    MATCH = True
except ImportError:
    MATCH = False

try:
    import ryzenai_onnx_utils.postprocess

    POSTPROCESS = True
except ImportError:
    POSTPROCESS = False

try:
    import ryzenai_onnx_utils.preprocess

    PREPROCESS = True
except ImportError:
    PREPROCESS = False

try:
    import ryzenai_onnx_utils.report

    REPORT = True
except ImportError:
    REPORT = False

try:
    import ryzenai_onnx_utils.auto

    AUTO = True
except ImportError:
    AUTO = False

try:
    import ryzenai_onnx_utils.vaiml

    VAIML = True
except ImportError:
    VAIML = False

try:
    import ryzenai_onnx_utils.transform.dd as dd
except ImportError:
    dd = None


def configure_parser(subparser):
    partition_parser = subparser.add_parser("partition")

    partition_parser.add_argument(
        "input_path", type=Path, help="Path to input ONNX model"
    )
    partition_parser.add_argument(
        "output_path", type=Path, help="Path to create directories for output files"
    )
    partition_parser.add_argument("strategy", type=Path, help="Strategy to run")
    partition_parser.add_argument(
        "--attributes",
        metavar="KEY=VALUE",
        nargs="+",
        help="Specify and override any strategy attributes as key=value pairs",
    )
    partition_parser.add_argument(
        "--dd-files-path",
        type=Path,
        default=Path(".cache"),
        help="Path to create DD files in, either absolute or relative to output_path",
    )
    partition_parser.add_argument(
        "--model-name", default="replaced", help="Name of the new onnx model"
    )
    partition_parser.add_argument(
        "--save-as-external",
        action="store_true",
        help="Save the model with external data",
    )
    partition_parser.add_argument(
        "--load-external-data",
        action="store_true",
        help="Load all external data at startup",
    )
    partition_parser.add_argument(
        "--passes-per-iteration",
        type=int,
        default=None,
        help="Run the passes in intervals, saving the model in between. Defaults to None",
    )
    partition_parser.add_argument(
        "--combine-dd",
        action="store_true",
        help="Combine generated DD files",
    )
    partition_parser.add_argument(
        "--force",
        action="store_true",
        help="Answer yes to any confirmations that may come up",
    )
    partition_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Print more messages",
    )


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--recursion-limit", default=10000, type=int, help="Recursion limit for Python"
    )
    parser.add_argument(
        "--external-data-extension",
        default="onnx.data",
        help="File extension for external data file",
    )
    subparsers = parser.add_subparsers(dest="subparser")

    configure_parser(subparsers)

    if MATCH:
        ryzenai_onnx_utils.matcher.configure_parser(subparsers)

    if EXTRACT:
        ryzenai_onnx_utils.extract.configure_parser(subparsers)

    if PREPROCESS:
        ryzenai_onnx_utils.preprocess.configure_parser(subparsers)

    if POSTPROCESS:
        ryzenai_onnx_utils.postprocess.configure_parser(subparsers)

    if REPORT:
        ryzenai_onnx_utils.report.configure_parser(subparsers)

    if AUTO:
        ryzenai_onnx_utils.auto.configure_parser(subparsers)

    if VAIML:
        ryzenai_onnx_utils.vaiml.configure_parser(subparsers)

    return parser


def print_verbose(message, verbose, level):
    if verbose >= level:
        print(message)


def replace(
    pattern,
    replacement,
    params: ryzenai_onnx_utils.ReplaceParams,
    extractor,
    pass_id: str,
    verbose,
    indent="",
    pass_name=None,
):
    onnx_matcher_quiet = verbose <= 1
    matcher = ryzenai_onnx_utils.matcher.Matcher(pattern, onnx_matcher_quiet)

    max_to_replace = None

    # Use a specific policy to build new subgraphs and replace matching subgraphs.
    replaced_num = matcher.replace(
        extractor, replacement, pass_id, params, max_to_replace
    )
    if replaced_num < 0:
        print_verbose(f"{indent}Finished pass", verbose, 1)
    else:
        print_verbose(f"{indent}Replaced {replaced_num} nodes", verbose, 1)
    return replaced_num


def _include_constructor(prefix_path: Path, loader: yaml.SafeLoader, node):
    yaml_files = loader.construct_sequence(node)
    name = Path(yaml_files.pop(0))
    if not name.is_absolute():
        name = prefix_path / name
    with open(name) as f:
        content = yaml.safe_load(f)
    for name in yaml_files:
        name = Path(name)
        if not name.is_absolute():
            name = prefix_path / name
        with open(name) as f:
            new_content = yaml.safe_load(f)
        for i in new_content:
            if isinstance(content[i], str):
                content[i] = new_content[i]
            elif isinstance(content[i], list):
                content[i].extend(new_content[i])
            else:
                raise ValueError("Unhandled type")
    return content


def load_strategy(strategy_path: Path):
    strategy_prefix = (
        importlib.resources.files("ryzenai_onnx_utils") / "data/partition_strategies"
    )
    if not strategy_path.is_absolute():
        strategy_file = strategy_prefix / strategy_path
    else:
        strategy_file = strategy_path
    include_constructor = functools.partial(_include_constructor, strategy_prefix)
    yaml.add_constructor("!include", include_constructor, Loader=yaml.SafeLoader)
    with open(strategy_file) as f:
        strategy = yaml.safe_load(f)
    if "passes" not in strategy:
        strategy["passes"] = []
    if "inherit_passes_before" in strategy:
        passes_after = copy.copy(strategy["passes"])
        strategy["passes"] = strategy["inherit_passes_before"]["passes"]
        strategy["passes"].extend(passes_after)
        del strategy["inherit_passes_before"]
    if "inherit_passes_after" in strategy:
        strategy["passes"].extend(strategy["inherit_passes_after"]["passes"])
        del strategy["inherit_passes_after"]
    if "postprocess" in strategy:
        strategy["passes"].extend(strategy["postprocess"])
        del strategy["postprocess"]
    return strategy


def make_hints(
    extractor: onnx.utils.Extractor,
    params: ryzenai_onnx_utils.ReplaceParams,
    hints_keys: Iterable[str],
) -> dict[str, list[onnx.NodeProto]]:
    xclbin_mapping = params.attributes["xclbins"]
    node_mapping: dict[str, list] = {}
    graph = extractor.graph
    for node in graph.node:
        if all(hints_key not in node.op_type for hints_key in hints_keys):
            continue
        if node.op_type in node_mapping:
            node_mapping[node.op_type].append(node)
        else:
            node_mapping[node.op_type] = [node]
    hints: dict[str, list] = {}
    if isinstance(xclbin_mapping, dict):
        for op_type, xclbin_path in xclbin_mapping.items():
            if op_type not in node_mapping:
                continue
            label = xclbin_path.split("/")[-1]
            if label in hints:
                hints[label] += node_mapping[op_type]
            else:
                hints[label] = node_mapping[op_type]
    elif isinstance(xclbin_mapping, str):
        hints[xclbin_mapping.split("/")[-1]] = []
        for node_list in node_mapping.values():
            hints[xclbin_mapping.split("/")[-1]] += node_list
    return hints


def partition(
    extractor: onnx.utils.Extractor,
    passes: list,
    params: ryzenai_onnx_utils.ReplaceParams,
    verbose: int,
    runtime_attributes: dict = None,
):
    def recurse(sub_graph: onnx.GraphProto):
        sub_model = onnx.helper.make_model(sub_graph, producer_name="from_subgraph")
        sub_extractor = ryzenai_onnx_utils.matcher.get_extractor(sub_model)
        sub_model, sub_total_replace_num = partition(
            sub_extractor, passes, params, verbose, runtime_attributes
        )
        return sub_total_replace_num, sub_model.graph

    if runtime_attributes is None:
        runtime_attributes = {}
    print_verbose("Starting passes...", verbose, 1)

    total_replaced_num = 0

    for node in extractor.graph.node:
        if node.op_type != "Constant":
            for attr in node.attribute:
                if attr.type == onnx.AttributeProto.GRAPH:
                    print_verbose(
                        f"Starting passes of {node.name, node.op_type}...", verbose, 1
                    )
                    replaced_num, new_subgraph = recurse(attr.g)
                    total_replaced_num += replaced_num
                    ryzenai_onnx_utils.matcher.set_attribute(
                        node, attr.name, new_subgraph
                    )
                    print_verbose(
                        f"End passes of {node.name, node.op_type}.", verbose, 1
                    )
                elif attr.type == onnx.AttributeProto.GRAPHS:
                    new_graphs = []
                    print_verbose(
                        f"Starting passes of {node.name, node.op_type}...", verbose, 1
                    )
                    for subgraph in attr.graphs:
                        replaced_num, new_subgraph = recurse(subgraph)
                        total_replaced_num += replaced_num
                        new_graphs.append(new_subgraph)
                    ryzenai_onnx_utils.matcher.set_attribute(
                        node, attr.name, new_graphs
                    )
                    print_verbose(
                        f"End passes of {node.name, node.op_type}.", verbose, 1
                    )

    for pass_index, run_pass in enumerate(passes):
        if isinstance(run_pass, str):
            pass_name = run_pass
            pass_attributes = {}
            pass_exclusions = {}
        else:
            pass_name = next(iter(run_pass))
            pass_attributes = run_pass[pass_name].get("attributes", {})
            pass_exclusions = run_pass[pass_name].get("exclude", {})
        pass_params = copy.deepcopy(params)
        pass_params.attributes = {
            **params.attributes,
            **pass_attributes,
            **runtime_attributes,
        }
        current_pass = importlib.import_module(f"ryzenai_onnx_utils.passes.{pass_name}")
        print_verbose(
            f"Starting pass {pass_name} ({pass_index+1} of {len(passes)})...",
            verbose,
            1,
        )
        if (
            current_pass.PATTERN  # ensure that there's at least one pattern
            and not callable(current_pass.PATTERN)  # and it's not a callable
            and not isinstance(current_pass.PATTERN[0], str)  # it has a nested pattern
            and callable(current_pass.REPLACEMENT)  #  it is a function not a list
        ):
            current_pass.REPLACEMENT = [current_pass.REPLACEMENT] * len(
                current_pass.PATTERN
            )
        if isinstance(current_pass.REPLACEMENT, list):
            assert len(current_pass.REPLACEMENT) == len(current_pass.PATTERN)
            for subpass_index, (pattern, replacement) in enumerate(
                zip(current_pass.PATTERN, current_pass.REPLACEMENT)
            ):
                if isinstance(pattern, SubPass):
                    subpass_name = pattern.name
                    pattern = pattern.pattern
                else:
                    subpass_name = (replacement.__module__).split(".")[-1]
                if subpass_name in pass_exclusions:
                    print_verbose(
                        f"  Skipping subpass {subpass_name} ({subpass_index+1} of {len(current_pass.REPLACEMENT)})...",
                        verbose,
                        1,
                    )
                    continue
                print_verbose(
                    f"  Starting subpass {subpass_name} ({subpass_index+1} of {len(current_pass.REPLACEMENT)})...",
                    verbose,
                    1,
                )
                replaced_num = replace(
                    pattern,
                    replacement,
                    pass_params,
                    extractor,
                    f"{pass_index}_{subpass_index}",
                    verbose,
                    "  ",
                    pass_name,
                )
                total_replaced_num += max(replaced_num, 0)
        elif callable(current_pass.PATTERN):
            # PATTERN(extractor, str, ReplaceParam) -> list[list[str]]
            # and REPLACEMENT(extractor, str, list[onnx.NodeProto], ReplaceParam)
            patterns = current_pass.PATTERN(extractor, pass_index, params)
            assert isinstance(patterns, list)
            if patterns:
                assert all(
                    isinstance(sublist, list)
                    and all(isinstance(item, str) for item in sublist)
                    for sublist in patterns
                )
            replacements = [current_pass.REPLACEMENT] * len(patterns)
            for subpass_index, (pattern, replacement) in enumerate(
                zip(patterns, replacements)
            ):
                replaced_num = replace(
                    pattern,
                    replacement,
                    pass_params,
                    extractor,
                    f"{pass_index}_{subpass_index}",
                    verbose,
                )
                total_replaced_num += max(replaced_num, 0)
        else:
            replaced_num = replace(
                current_pass.PATTERN,
                current_pass.REPLACEMENT,
                pass_params,
                extractor,
                str(pass_index),
                verbose,
                "",
                pass_name,
            )
            total_replaced_num += max(replaced_num, 0)
    print_verbose(
        f"Replaced {total_replaced_num} nodes in total across {len(passes)} passes",
        verbose,
        1,
    )

    if total_replaced_num > 0:
        domains = params.get_domains()
        for domain in domains:
            ryzenai_onnx_utils.matcher.set_opset(extractor.model, domain, 1)

    try:
        ryzenai_onnx_utils.matcher.graph_topological_sort(extractor, True)
    except RuntimeError as e:
        print("*** This graph is invalid. Examine the saved model: " + str(e))

    return extractor.model, total_replaced_num


def _run_manual_passes(
    input_path: Path,
    output_path: Path,
    save_as_external: bool,
    location: str,
    passes: list,
):
    if not passes:
        return
    onnx_model = onnx.load_model(input_path)
    extractor = ryzenai_onnx_utils.matcher.get_extractor(onnx_model)
    params = ryzenai_onnx_utils.ReplaceParams(
        {"xclbins": "", "domains": "ai.onnx", "op_namespaces": ""},
        output_path,
        "",
        "",
    )
    model, total_replaced_num = partition(extractor, passes, params, True)
    if total_replaced_num > 0:
        ryzenai_onnx_utils.matcher.save_external_data_with_extractor(
            model, extractor, location, output_path.parent, save_as_external
        )
        ryzenai_onnx_utils.matcher.save_model_without_external_data(model, output_path)


def confirm(prompt):
    answer = ""
    while answer not in ["y", "n", "yes", "no"]:
        answer = input(prompt).lower()
    return answer in ["y", "yes"]


def confirm_or_exit(prompt, force):
    if force:
        print(prompt, "Y")
    elif not confirm(prompt):
        print("Exiting")
        sys.exit(0)


def parse_runtime_attributes(attributes: Optional[list]):
    attributes_dict = {}
    if attributes is not None:
        for attribute in attributes:
            if "=" not in attribute:
                raise ValueError(f"Invalid attribute key-value provided: {attribute}")
            split_string = attribute.split("=")
            attributes_dict[split_string[0].strip()] = split_string[1].strip()
    return attributes_dict


def partition_main(args):
    input_path: Path = args.input_path
    output_path: Path = args.output_path
    dd_files_path: Path = args.dd_files_path
    strategy_path = args.strategy
    save_as_external = args.save_as_external
    verbose = args.verbose
    runtime_attributes = parse_runtime_attributes(args.attributes)

    input_path = input_path.absolute()
    output_path = output_path.absolute()

    output_model_path = output_path / f"{args.model_name}.onnx"
    if output_model_path.exists():
        prompt = f"{str(output_model_path)} exists. Okay to overwrite? (y|n) "
        confirm_or_exit(prompt, args.force)
    curr_output_model = output_path / "tmp_0.onnx"
    next_output_model = output_path / "tmp_1.onnx"

    dd_files_path_abs = (
        dd_files_path if dd_files_path.is_absolute() else output_path / dd_files_path
    )
    if dd_files_path_abs.exists():
        prompt = (
            f"{str(dd_files_path_abs)} exists. Delete directory and continue? (y|n) "
        )
        confirm_or_exit(prompt, args.force)
        shutil.rmtree(dd_files_path_abs)

    # this directory gets deleted and created by the build_dd_node function
    # when creating the DD files. If DD can generate files in the output path
    # directly, we can delete this
    delete_dd_files_path = False
    if not dd_files_path.is_absolute():
        if dd_files_path.exists():
            prompt = f"{str(dd_files_path)} exists. Continue? (y|n) "
            confirm_or_exit(prompt, args.force)
        else:
            delete_dd_files_path = True
            dd_files_path.mkdir(parents=True, exist_ok=True)

    output_path.mkdir(parents=True, exist_ok=True)
    dd_files_path_abs.mkdir(parents=True, exist_ok=True)

    strategy = load_strategy(strategy_path)
    params = ryzenai_onnx_utils.ReplaceParams(
        strategy["attributes"], output_model_path, dd_files_path, dd_files_path_abs
    )

    passes_per_iteration = args.passes_per_iteration
    if passes_per_iteration is None or passes_per_iteration < 1:
        passes_per_iteration = len(strategy["passes"])
        run_all_passes = True
    else:
        print_verbose(
            f"Running passes iteratively {passes_per_iteration} at a time...",
            verbose,
            1,
        )
        run_all_passes = False

    any_replaced = False
    for i in range(0, len(strategy["passes"]), passes_per_iteration):
        stop_index = min(i + passes_per_iteration, len(strategy["passes"]))

        print_verbose("Loading model...", verbose, 1)
        try:
            extractor = ryzenai_onnx_utils.matcher.load_extractor(
                input_path, args.load_external_data
            )
        except onnx.onnx_cpp2py_export.shape_inference.InferenceError:
            print_verbose("Shape inference failed, continuing...", verbose, 1)
            extractor = ryzenai_onnx_utils.matcher.load_extractor(
                input_path, args.load_external_data, False
            )
        del extractor.model.graph.initializer[:]
        print_verbose("Loaded model", verbose, 1)

        model, total_replaced_num = partition(
            extractor,
            strategy["passes"][i:stop_index],
            params,
            verbose,
            runtime_attributes,
        )

        if total_replaced_num > 0:
            any_replaced = True
            if not run_all_passes:
                print_verbose("Saving temporary model...", verbose, 1)
                external_data_name = (
                    f"{curr_output_model.stem}.{args.external_data_extension}"
                )
                ryzenai_onnx_utils.matcher.save_external_data_with_extractor(
                    model,
                    extractor,
                    external_data_name,
                    output_model_path.parent,
                    save_as_external,
                )

                ryzenai_onnx_utils.matcher.save_model_without_external_data(
                    model, curr_output_model
                )
                print_verbose("Saved temporary model", verbose, 1)

                input_path = copy.copy(curr_output_model)
                curr_output_model = copy.copy(next_output_model)
                next_output_model = copy.copy(input_path)

    if any_replaced:
        print_verbose("Saving final model...", verbose, 1)
        if not run_all_passes:
            try:
                extractor = ryzenai_onnx_utils.matcher.load_extractor(
                    input_path, args.load_external_data
                )
            except onnx.onnx_cpp2py_export.shape_inference.InferenceError:
                print_verbose("Shape inference failed, continuing...", verbose, 1)
                extractor = ryzenai_onnx_utils.matcher.load_extractor(
                    input_path, args.load_external_data, False
                )
        else:
            # reset the model with the updated model returned from the partitioner
            extractor.model = model

        external_data_name = f"{args.model_name}.{args.external_data_extension}"
        ryzenai_onnx_utils.matcher.save_external_data_with_extractor(
            extractor.model,
            extractor,
            external_data_name,
            output_model_path.parent,
            save_as_external,
        )

        ryzenai_onnx_utils.matcher.save_model_without_external_data(
            extractor.model, output_model_path
        )

        print_verbose("Saved final model", verbose, 1)

        if args.combine_dd:
            assert dd is not None, "DD Python library could not be imported"
            print_verbose("Combining DD files...", verbose, 1)
            dd.combine_dd(dd_files_path, dd_files_path_abs, output_path)
            print_verbose("Combined DD files", verbose, 1)

        # onnx.checker.check_model(output_path / "replaced.onnx", full_check=True)

    if delete_dd_files_path:
        shutil.rmtree(dd_files_path)

    ryzenai_onnx_utils.matcher.delete_model(
        curr_output_model, args.external_data_extension
    )
    ryzenai_onnx_utils.matcher.delete_model(
        next_output_model, args.external_data_extension
    )


def pattern_match(args):
    model = pb.get_model(
        args.input_path,
        args.extract_inputs,
        args.extract_outputs,
        args.load_external_data,
    )
    extractor = ryzenai_onnx_utils.matcher.get_extractor(model)
    original_pattern = pb.convert_model_to_pattern(model)
    if args.strategy:
        print("Pattern before partitioner:")
        print(original_pattern)

        strategy = load_strategy(args.strategy)
        passes = strategy["passes"]
        if any(pass_name.startswith("dd") for pass_name in passes):
            raise ValueError("DD passes are not supported to run here")
        params = ryzenai_onnx_utils.ReplaceParams(
            strategy["attributes"],
            Path(),
            Path(),
            Path(),
        )
        model, _ = partition(extractor, passes, params, 0)
        new_patterns = []
        if args.hints_key:
            hints = make_hints(extractor, params, args.hints_key)
            engine = pg.PartitionGraph(extractor, hints, args.hints_key)
            engine.partition()
            pattern_ = pg.PatternGenerator(engine)
            new_patterns = pattern_.get_patterns()
        else:
            new_patterns = pb.convert_model_to_pattern(model)
        print("Pattern after partitioner:")
        print(new_patterns)
    else:
        print("Pattern:")
        print(original_pattern)


def main():
    parser = get_parser()
    args = parser.parse_args()

    sys.setrecursionlimit(args.recursion_limit)

    if args.subparser == "partition":
        partition_main(args)
    elif args.subparser == "match":
        pattern_match(args)
    elif args.subparser == "extract":
        if args.pattern_file:
            user_pattern = ryzenai_onnx_utils.utils.load_module_from_file(
                args.pattern_file, "user_pattern"
            )
            args.pattern = user_pattern.user_pattern
        elif args.pattern.startswith("op-"):
            name = args.pattern.removeprefix("op-")
            spec = importlib.util.spec_from_file_location(
                "user_pattern",
                importlib.resources.files("ryzenai_onnx_utils")
                / "data/extract_patterns/op.py",
            )
            user_pattern = importlib.util.module_from_spec(spec)
            sys.modules["user_pattern"] = user_pattern
            spec.loader.exec_module(user_pattern)
            args.pattern = functools.partial(user_pattern.op, name)
        else:
            assert args.pattern != "op", "Use op-<name> to match on a particular op"
            spec = importlib.util.spec_from_file_location(
                "user_pattern",
                importlib.resources.files("ryzenai_onnx_utils")
                / f"data/extract_patterns/{args.pattern}.py",
            )
            user_pattern = importlib.util.module_from_spec(spec)
            sys.modules["user_pattern"] = user_pattern
            spec.loader.exec_module(user_pattern)
            args.pattern = user_pattern.user_pattern

        ryzenai_onnx_utils.extract.main(args)
    elif args.subparser == "postprocess":
        ryzenai_onnx_utils.postprocess.main(args)
    elif args.subparser == "preprocess":
        ryzenai_onnx_utils.preprocess.main(args)
    elif args.subparser == "report":
        ryzenai_onnx_utils.report.main(args)
    elif args.subparser == "auto":
        ryzenai_onnx_utils.auto.main(args)
    elif args.subparser == "vaiml":
        ryzenai_onnx_utils.vaiml.main(args)
    else:
        raise ValueError(f"Unknown subparser: {args.subparser}")
