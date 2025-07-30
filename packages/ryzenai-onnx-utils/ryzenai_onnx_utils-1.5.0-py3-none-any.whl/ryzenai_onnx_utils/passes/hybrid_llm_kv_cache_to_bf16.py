# Copyright (c) 2024 Advanced Micro Devices, Inc.

import onnx

import ryzenai_onnx_utils.matcher
import ryzenai_onnx_utils.transform.hybrid_llm
from ryzenai_onnx_utils.passes import global_pass


@global_pass
def convert_kv_cache(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    for node in extractor.graph.node:
        if node.op_type == "GQO":
            k_shape = ryzenai_onnx_utils.matcher.get_shape(node.input[1], extractor)
            input_names = node.input[1:3]
            input_tvis = []
            for kv_name in input_names:
                input_tvis.append(
                    onnx.helper.make_tensor_value_info(
                        kv_name, onnx.TensorProto.BFLOAT16, k_shape
                    )
                )
            output_names = node.output[:2]
            output_tvis = []
            for kv_name in output_names:
                output_tvis.append(
                    onnx.helper.make_tensor_value_info(
                        kv_name, onnx.TensorProto.BFLOAT16, k_shape
                    )
                )

            ryzenai_onnx_utils.matcher.remove_graph_inputs(input_names, extractor.graph)
            ryzenai_onnx_utils.matcher.remove_graph_outputs(
                output_names, extractor.graph
            )

            extractor.graph.input.extend(input_tvis)
            extractor.graph.output.extend(output_tvis)


REPLACEMENT = convert_kv_cache
PATTERN = []
