"""Utility functions for project dependency management."""

from __future__ import annotations

import ast
import logging
import sys
from pathlib import Path
from typing import Iterable
import tomllib


def find_dependency_file(start: Path) -> Path | None:
    """Return nearest requirements.txt or pyproject.toml searching upwards."""
    current = start.resolve()
    for parent in [current] + list(current.parents):
        req = parent / "requirements.txt"
        if req.exists():
            return req
        proj = parent / "pyproject.toml"
        if proj.exists():
            return proj
    return None


def _parse_requirements(lines: Iterable[str]) -> list[str]:
    deps: list[str] = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        deps.append(line)
    return deps


def parse_dependencies(path: Path) -> list[str]:
    """Return dependency strings from *path*."""
    if path.name == "requirements.txt":
        return _parse_requirements(path.read_text().splitlines())
    if path.name == "pyproject.toml":
        data = tomllib.loads(path.read_text())
        return list(data.get("project", {}).get("dependencies", []))
    return []


def dependency_names(dependencies: Iterable[str]) -> set[str]:
    """Extract package names from dependency strings."""
    names: set[str] = set()
    for dep in dependencies:
        name = dep.split(";")[0]
        for sep in ["==", ">=", "<=", ">", "<"]:
            name = name.split(sep)[0]
        name = name.split("[")[0].strip()
        if name:
            names.add(name)
    return names


def warn_missing_imports(
    source: str, available: set[str], logger: logging.Logger
) -> None:
    """Warn if *source* imports packages not in *available*."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return

    stdlib = sys.stdlib_module_names

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in available and root not in stdlib:
                    logger.warning(
                        f"Generated code imports '{root}' not listed in project dependencies"
                    )
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            if root not in available and root not in stdlib:
                logger.warning(
                    f"Generated code imports '{root}' not listed in project dependencies"
                )


__all__ = [
    "find_dependency_file",
    "parse_dependencies",
    "dependency_names",
    "warn_missing_imports",
]
