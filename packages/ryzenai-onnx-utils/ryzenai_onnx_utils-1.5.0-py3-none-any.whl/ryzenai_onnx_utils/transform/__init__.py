# Copyright (c) 2024 Advanced Micro Devices, Inc.

import contextlib

with contextlib.suppress(ImportError):
    from .dd import build_dd_node
