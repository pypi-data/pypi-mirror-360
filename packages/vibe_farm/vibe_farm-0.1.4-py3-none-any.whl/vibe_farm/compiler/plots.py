# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
"""Utilities for extracting farmed function plots."""

from __future__ import annotations
from vibe_farm.__about__ import __license__, __copyright__

import ast
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from ..analysis import ast_utils


@dataclass
class FunctionPlot:
    """A farmed function or method plot."""

    qualname: str
    node: ast.FunctionDef
    source: str
    file_path: Path


def extract_plots(path: Path, module_ast: ast.Module) -> list[FunctionPlot]:
    """Return plots for all farmed functions or methods in *module_ast*."""

    imported_code = ast_utils.get_vibefarm_imported_code(module_ast)

    class Collector(ast.NodeVisitor):
        def __init__(self) -> None:
            self.plots: list[FunctionPlot] = []
            self.class_stack: list[str] = []

        def visit_ClassDef(
            self, node: ast.ClassDef
        ) -> None:  # noqa: D401 - short description
            """Collect plots from class body."""
            self.class_stack.append(node.name)
            self.generic_visit(node)
            self.class_stack.pop()

        def visit_FunctionDef(
            self, node: ast.FunctionDef
        ) -> None:  # noqa: D401 - short description
            """Check function for farm decoration and code raises."""
            if _is_farm_decorated(node) and ast_utils.find_raises_of_vibecode(
                node, imported_code
            ):
                qualname = (
                    ".".join(self.class_stack + [node.name])
                    if self.class_stack
                    else node.name
                )
                plot_src = create_plot_source(node)
                self.plots.append(FunctionPlot(qualname, node, plot_src, path))
            self.generic_visit(node)

    collector = Collector()
    collector.visit(module_ast)
    return collector.plots


# Implementation details -----------------------------------------------------


def _is_farm_decorated(fn: ast.FunctionDef) -> bool:
    for dec in fn.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "farm":
            return True
        if isinstance(dec, ast.Attribute) and dec.attr == "farm":
            return True
    return False


def create_plot_source(node: ast.FunctionDef, source: str | None = None) -> str:
    """Return source for *node* with farm decorations stripped."""

    if source is not None and ast.get_source_segment(source, node) is None:
        return ""

    todo_count = 0
    plot_node = deepcopy(node)
    plot_node.decorator_list = [
        d
        for d in plot_node.decorator_list
        if not (
            (isinstance(d, ast.Name) and d.id == "farm")
            or (isinstance(d, ast.Attribute) and d.attr == "farm")
        )
    ]

    new_body: list[ast.stmt] = []
    for stmt in plot_node.body:
        if _is_raise_code(stmt):
            todo_count += 1
            new_body.append(ast.Pass())
        else:
            new_body.append(stmt)
    plot_node.body = new_body

    text = ast.unparse(plot_node)

    if todo_count:
        lines = text.splitlines()
        replaced = 0
        for i, line in enumerate(lines):
            if line.strip() == "pass":
                indent = line[: len(line) - len(line.lstrip())]
                lines[i] = f"{indent}# TODO"
                replaced += 1
                if replaced == todo_count:
                    break
        text = "\n".join(lines)
    return text


def _is_raise_code(node: ast.stmt) -> bool:
    return (
        isinstance(node, ast.Raise)
        and isinstance(node.exc, ast.Call)
        and isinstance(node.exc.func, ast.Name)
        and node.exc.func.id == "code"
    )


def apply_generated_code(plot: FunctionPlot, code: str) -> None:
    """Replace ``raise code()`` with *code* in *plot.node*."""

    plot.node.decorator_list = [
        d
        for d in plot.node.decorator_list
        if not (
            (isinstance(d, ast.Name) and d.id == "farm")
            or (isinstance(d, ast.Attribute) and d.attr == "farm")
        )
    ]

    generated_body = ast.parse(code).body

    new_body: list[ast.stmt] = []
    for stmt in plot.node.body:
        if _is_raise_code(stmt):
            new_body.extend(generated_body)
        else:
            new_body.append(stmt)
    plot.node.body = new_body


__all__ = [
    "FunctionPlot",
    "extract_plots",
    "create_plot_source",
    "apply_generated_code",
]
