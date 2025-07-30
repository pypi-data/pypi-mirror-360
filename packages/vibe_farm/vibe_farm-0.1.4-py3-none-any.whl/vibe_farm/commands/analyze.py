# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
from vibe_farm.__about__ import __license__, __copyright__

"""
Analyze command implementation for vibe_farm CLI.
"""

from pathlib import Path
from .utils import gather_python_sources


def analyze_command(sources: list[Path]) -> None:
    """
    Analyze the specified Vibe source files.

    Args:
        sources: List of source files or directories to analyze.
    """
    from ..analysis import analyze_vibe_sources

    expanded_sources = gather_python_sources(sources)

    # Analyze the sources
    results = analyze_vibe_sources(expanded_sources)
    for src, count in results.items():
        print(f"Found {count} raise code() statements in {src}")
