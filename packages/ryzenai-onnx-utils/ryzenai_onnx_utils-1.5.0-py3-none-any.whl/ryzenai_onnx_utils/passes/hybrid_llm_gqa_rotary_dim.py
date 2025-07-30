# Copyright (c) 2024 Advanced Micro Devices, Inc.

"""
The ORT CPU version of GQA does not support an attribute called
"rotary_embedding_dim" so remove it. It is added when rotary embedding is fused
into GQA before it's converted to GQO.
"""

import onnx

import ryzenai_onnx_utils.matcher


def replacement(
    extractor: onnx.utils.Extractor,
    pass_id: str,
    subgraph: list[onnx.NodeProto],
    params: ryzenai_onnx_utils.ReplaceParams,
):
    ryzenai_onnx_utils.matcher.delete_attribute(subgraph[0], "rotary_embedding_dim")
    return subgraph, [], None


PATTERN = [
    "GroupQueryAttention([?,?,?,?,?,?,?,?,?], [?,?,?])",
]
REPLACEMENT = replacement
