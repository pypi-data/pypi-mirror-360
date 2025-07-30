# Copyright (c) 2024 Advanced Micro Devices, Inc.

import importlib
from pathlib import Path
from typing import Optional

import ryzenai_onnx_utils.utils


def configure_parser(subparser):
    postprocess_parser = subparser.add_parser("postprocess")
    postprocess_parser.add_argument(
        "--input-path", type=Path, nargs="+", help="Path to input ONNX model"
    )
    postprocess_parser.add_argument(
        "--output-path",
        type=Path,
        help="Path to output ONNX model",
    )
    postprocess_parser.add_argument(
        "script",
        type=Path,
        help="Name of the script to run",
    )
    postprocess_parser.add_argument(
        "--attributes",
        metavar="KEY=VALUE",
        nargs="+",
        help="Specify any attributes as key=value pairs",
    )

    return postprocess_parser


def parse_runtime_attributes(attributes: Optional[list]):
    attributes_dict = {}
    if attributes is not None:
        for attribute in attributes:
            if "=" not in attribute:
                raise ValueError(f"Invalid attribute key-value provided: {attribute}")
            split_string = attribute.split("=")
            attributes_dict[split_string[0].strip()] = split_string[1].strip()
    return attributes_dict


def main(args):
    script: Path = args.script

    if script.is_absolute():
        module = ryzenai_onnx_utils.utils.load_module_from_file(script, "module")
    else:
        module = importlib.import_module(
            f"ryzenai_onnx_utils.model_postprocessing.{script}"
        )

    runtime_attributes = parse_runtime_attributes(args.attributes)
    runtime_attributes["external_data_extension"] = args.external_data_extension

    module.postprocess(args.input_path, args.output_path, runtime_attributes)
