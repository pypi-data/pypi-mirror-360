# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
"""Context gathering strategies for farmed plots."""

from __future__ import annotations
from vibe_farm.__about__ import __license__, __copyright__

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .plots import FunctionPlot
from .. import dependencies as dep_utils


@dataclass
class ContextItem:
    """Related source context for a plot."""

    path: Path
    start_line: int
    end_line: int
    source: str


@dataclass
class PlotContext:
    """A plot paired with gathered context."""

    plot: FunctionPlot
    items: list[ContextItem]


class ContextGatherer(Protocol):
    """Protocol for context gathering strategies."""

    def gather(
        self, plot: FunctionPlot, module_ast: ast.Module, module_source: str
    ) -> list[ContextItem]:
        """Return context for *plot* within *module_source*."""
        ...  # pragma: no cover


class ModuleContextGatherer:
    """Return module source excluding the plot itself."""

    def gather(
        self, plot: FunctionPlot, module_ast: ast.Module, module_source: str
    ) -> list[ContextItem]:
        lines = module_source.splitlines()
        start = plot.node.lineno
        if plot.node.decorator_list:
            start = min(dec.lineno for dec in plot.node.decorator_list)
        end = plot.node.end_lineno

        placeholder = self._placeholder_source(plot)
        context_lines = lines[: start - 1] + placeholder.splitlines() + lines[end:]
        context_source = "\n".join(context_lines)
        return [ContextItem(plot.file_path, 1, len(context_lines), context_source)]

    @staticmethod
    def _placeholder_source(plot: FunctionPlot) -> str:
        # Build FunctionDef for Python 3.12+
        node = ast.FunctionDef(
            name=plot.node.name,
            args=plot.node.args,
            body=[
                ast.Expr(
                    value=ast.Constant(
                        f"TODO: Generated implementation of {plot.qualname} goes here."
                    )
                )
            ],
            decorator_list=[],
            returns=plot.node.returns,
            type_comment=plot.node.type_comment,
            type_params=[],
        )

        node = ast.fix_missing_locations(node)

        text = ast.unparse(node)
        indent = " " * plot.node.col_offset
        if indent:
            text = "\n".join(
                indent + line if line else line for line in text.splitlines()
            )
        return text


class ImportContextGatherer:
    """Gather context for imported symbols used in the module."""

    def gather(
        self, plot: FunctionPlot, module_ast: ast.Module, module_source: str
    ) -> list[ContextItem]:
        import inspect
        import importlib

        items: list[ContextItem] = []
        package = self._module_package(plot.file_path)
        base_path = plot.file_path

        for node in module_ast.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("vibe_farm"):
                        continue  # pragma: no cover - skip library hooks
                    items.extend(self._context_for_name(alias.name, package, base_path))
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("vibe_farm"):
                    continue
                module = "." * node.level + (node.module or "")
                for alias in node.names:
                    if module.startswith("vibe_farm") or alias.name.startswith(
                        "vibe_farm"
                    ):
                        continue  # pragma: no cover - skip library hooks
                    items.extend(
                        self._context_for_name(
                            f"{module}.{alias.name}", package, base_path
                        )
                    )

        return items

    @staticmethod
    def _module_package(path: Path) -> str | None:
        parts: list[str] = []
        parent = path.parent
        while (parent / "__init__.py").exists():  # pragma: no cover - rarely nested
            parts.append(parent.name)
            parent = parent.parent
        return ".".join(reversed(parts)) if parts else None

    def _context_for_name(
        self, dotted: str, package: str | None, base: Path
    ) -> list[ContextItem]:
        import inspect
        import importlib
        from pathlib import Path

        try:
            module_name, _, attr = dotted.rpartition(".")
            if dotted.startswith("."):
                mod = importlib.import_module(
                    module_name or "." + attr, package=package
                )
                obj = getattr(mod, attr) if module_name else mod
            else:
                mod = (
                    importlib.import_module(module_name)
                    if module_name
                    else importlib.import_module(attr)
                )
                obj = getattr(mod, attr) if module_name else mod
        except Exception:
            if dotted.startswith("."):
                return self._context_from_path(dotted, base)
            return []

        try:
            source = inspect.getsource(obj)
            path = Path(inspect.getsourcefile(obj) or "<unknown>")
            lines, start = inspect.getsourcelines(obj)
            end = start + len(lines) - 1
            return [ContextItem(path, start, end, source)]
        except Exception:
            doc = inspect.getdoc(obj) or ""
            sig = ""
            if callable(obj):
                try:
                    sig = str(inspect.signature(obj))
                except Exception:
                    sig = ""
            text = ((sig + "\n") if sig else "") + doc
            if not text:
                return []
            lines = text.splitlines()
            return [ContextItem(Path("<builtin>"), 1, len(lines), text)]

    def _context_from_path(self, dotted: str, base: Path) -> list[ContextItem]:
        """Attempt to load context from a path relative to *base*."""
        module_name, _, attr = dotted.rpartition(".")
        module_name = module_name.lstrip(".")
        path = base.parent
        if module_name:
            for part in module_name.split("."):
                path = path / part
            file = path.with_suffix(".py")
            if not file.exists():  # pragma: no cover - missing file
                file = path / "__init__.py"
                if not file.exists():
                    return []  # pragma: no cover - missing file
        else:
            file = (path / attr).with_suffix(".py")  # pragma: no cover - missing file
            if not file.exists():  # pragma: no cover - missing file
                file = path / attr / "__init__.py"
                if not file.exists():
                    return []  # pragma: no cover - missing file
        source = file.read_text()
        try:
            tree = ast.parse(source)
        except Exception:  # pragma: no cover - parse failure
            return []
        obj_name = attr if file.name != "__init__.py" else ""
        if obj_name:
            for node in tree.body:
                if (
                    isinstance(
                        node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                    )
                    and node.name == obj_name
                ):
                    assert node.lineno is not None and node.end_lineno is not None
                    start = node.lineno
                    end = node.end_lineno
                    lines = source.splitlines()
                    snippet = "\n".join(lines[start - 1 : end])
                    return [ContextItem(file, start, end, snippet)]
        return [
            ContextItem(file, 1, len(source.splitlines()), source)
        ]  # pragma: no cover


class DependencyContextGatherer:
    """Gather context about project dependencies."""

    def __init__(self, dependencies: list[str] | None, path: Path | None) -> None:
        self._dependencies = dependencies or []
        self._path = path

    def gather(
        self, plot: FunctionPlot, module_ast: ast.Module, module_source: str
    ) -> list[ContextItem]:
        if not self._dependencies or self._path is None:
            return []

        text = "\n".join(["Project dependencies:", *sorted(self._dependencies)])
        lines = text.splitlines()
        return [ContextItem(self._path, 1, len(lines), text)]


__all__ = [
    "ContextItem",
    "PlotContext",
    "ContextGatherer",
    "ModuleContextGatherer",
    "ImportContextGatherer",
    "DependencyContextGatherer",
]
