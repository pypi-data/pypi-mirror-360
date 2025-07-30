# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
from vibe_farm.__about__ import __license__, __copyright__

"""
AST analysis and utilities for vibe_farm.
"""

import ast
from pathlib import Path


def parse_python_file(file_path: Path) -> ast.Module:
    """Parse a Python file and return its AST module."""
    with file_path.open("r", encoding="utf-8") as f:
        source = f.read()
    return ast.parse(source, filename=str(file_path))


def find_raises_of_vibecode(tree: ast.AST, imported_code: set[str]) -> list[ast.Raise]:
    """
    Find all `raise code()` nodes in the AST where `code` is imported from vibe_farm.
    Returns a list of ast.Raise nodes.
    """
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            exc = node.exc
            if (
                isinstance(exc, ast.Call)
                and isinstance(exc.func, ast.Name)
                and exc.func.id in imported_code
            ):
                results.append(node)
    return results


def get_vibefarm_imported_code(tree: ast.AST) -> set[str]:
    """
    Return the set of names imported from vibe_farm in the AST.
    """
    code = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "vibe_farm":
            for alias in node.names:
                code.add(alias.asname or alias.name)
    return code
