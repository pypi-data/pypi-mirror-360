# Copyright (c) 2024 Advanced Micro Devices, Inc.

from typing import Union

from .pattern import Pattern


class Lexer:
    def __init__(self, patterns: Union[str, list[str]]):
        # Remove spaces and split patterns by the break line.
        if isinstance(patterns, str):
            lines = [
                item for item in patterns.replace(" ", "").split("\n") if item != ""
            ]
        else:
            lines = [item.replace(" ", "") for item in patterns]
        self.lines = lines

        # Parsing patterns by lexical analyzer.
        self.patterns: list[Pattern] = []
        self.edges = {}
        self.operators = {}
        for line in lines:
            pattern = Pattern(line)
            self.patterns.append(pattern)
            if pattern.name not in self.operators:
                self.operators[pattern.name] = 0
            self.operators[pattern.name] += 1

        named_operators = {k: v for k, v in self.operators.items() if k != "?"}
        self.anchor: str = (
            min(named_operators, key=self.operators.get) if named_operators else "?"
        )

        self.edges = self._build_edges()

    def _build_edges(self):
        edges = {}
        for index, pattern in enumerate(self.patterns):
            operator_names = pattern.name
            inputs = pattern.inputs
            outputs = pattern.outputs
            for io_num, io in enumerate(inputs):
                if io != "?":
                    if io not in edges:
                        edges[io] = {"src": [], "dst": []}
                    edges[io]["dst"].append(
                        {
                            "name": operator_names,
                            "pattern_index": index,
                            "io_index": io_num,
                        }
                    )
            for io_num, io in enumerate(outputs):
                if io != "?":
                    if io not in edges:
                        edges[io] = {"src": [], "dst": []}
                    edges[io]["src"].append(
                        {
                            "name": operator_names,
                            "pattern_index": index,
                            "io_index": io_num,
                        }
                    )
        return edges

    def op_in_pattern(self, op):
        return op in self.operators or "?" in self.operators

    def get_patterns_by_name(self, op, include_wildcards=True):
        patterns = []
        for index, pattern in enumerate(self.patterns):
            if (include_wildcards and pattern.name == "?") or pattern.name == op:
                patterns.append((pattern, index))
        return patterns

    def get_pattern_by_index(self, pattern_index):
        return [(self.patterns[pattern_index], pattern_index)]

    def get_named_io(self, pattern: Pattern):
        named_inputs = []
        named_outputs = []
        for io in pattern.inputs:
            if io != "?":
                named_inputs.append(io)
        for io in pattern.outputs:
            if io != "?":
                named_outputs.append(io)

        return named_inputs, named_outputs
