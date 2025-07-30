# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
"""Utility functions for command modules."""

from __future__ import annotations
from vibe_farm.__about__ import __license__, __copyright__

import sys
import subprocess
import importlib.util
from pathlib import Path


def gather_python_sources(sources: list[Path]) -> list[Path]:
    """Expand directories and validate python source files.

    Args:
        sources: List of files or directories.

    Returns:
        A list of Python source files discovered from the provided paths.
    """
    expanded: list[Path] = []
    for src in sources:
        if src.is_dir():
            expanded.extend(src.rglob("*.py"))
        else:
            expanded.append(src)

    for src in expanded:
        if not src.exists():
            print(f"Error: Source file '{src}' does not exist.", file=sys.stderr)
            sys.exit(1)

    filtered = [p for p in expanded if not p.name.endswith(".vibe.py")]

    return filtered


def post_process_vibe_files(vibe_files: list[Path]) -> None:
    """Format compiled vibe files using black if available."""

    if not vibe_files:
        return

    try:
        if importlib.util.find_spec("black") is None:
            return
    except Exception:  # pragma: no cover - best effort detection
        return

    subprocess.run(
        [sys.executable, "-m", "black", "--quiet", *[str(f) for f in vibe_files]],
        check=False,
    )


__all__ = ["gather_python_sources", "post_process_vibe_files"]
