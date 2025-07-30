# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
from vibe_farm.__about__ import __license__, __copyright__

"""Analysis utilities for ``vibe_farm``."""

from pathlib import Path
from . import ast_utils


def analyze_vibe_sources(sources: list[Path]) -> dict[Path, int]:
    """Analyze Vibe source files for ``raise code()`` statements."""
    results: dict[Path, int] = {}
    for src in sources:
        tree = ast_utils.parse_python_file(src)
        imported_code = ast_utils.get_vibefarm_imported_code(tree)
        raises = ast_utils.find_raises_of_vibecode(tree, imported_code)
        results[src] = len(raises)
    return results


__all__ = ["analyze_vibe_sources", "ast_utils"]
