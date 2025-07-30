# Copyright (c) 2025 Advanced Micro Devices, Inc.

import onnx

import ryzenai_onnx_utils
import ryzenai_onnx_utils.partitioner
import ryzenai_onnx_utils.pattern
import ryzenai_onnx_utils.pattern_generator as pg
from ryzenai_onnx_utils.transform.dd import build_dd_node


def generate_pattern(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    params: ryzenai_onnx_utils.ReplaceParams,
) -> list[list[str]]:
    hints_key = {"MladfMatMul", "FlatMLP", "FlatRMSAdd", "FLATMHA"}
    hints = ryzenai_onnx_utils.partitioner.make_hints(extractor, params, hints_key)
    engine = pg.PartitionGraph(extractor, hints, hints_key)
    engine.partition()
    pattern_ = pg.PatternGenerator(engine)
    patterns = pattern_.get_patterns()
    assert len(patterns) == 1
    # for LLMs, we have a "floating" v_matmul on the front that doesn't match
    # otherwise so insert a parent cast so we can match correctly
    patterns[0].insert(0, "CastAvx(?, b0)")

    matmul_0 = ryzenai_onnx_utils.pattern.Pattern(patterns[0][1])
    matmul_0.inputs[0] = "b0"
    patterns[0][1] = str(matmul_0)

    matmul_1 = ryzenai_onnx_utils.pattern.Pattern(patterns[0][2])
    matmul_1.inputs[0] = "b0"
    patterns[0][2] = str(matmul_1)

    return patterns


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    dd_node = build_dd_node(
        extractor,
        subgraph[1:],
        params,
    )

    return [subgraph[0], dd_node], [], None


PATTERN = generate_pattern
REPLACEMENT = replacement
