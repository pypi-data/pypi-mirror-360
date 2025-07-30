# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
from vibe_farm.__about__ import __license__, __copyright__

"""Compiler internals for the ``vibe_farm`` CLI."""

from .plots import (
    FunctionPlot,
    extract_plots,
    create_plot_source,
)
from .context import (
    ContextItem,
    PlotContext,
    ContextGatherer,
    ModuleContextGatherer,
    ImportContextGatherer,
    DependencyContextGatherer,
)
from .verification import (
    VerificationResult,
    PlotVerifier,
    ModuleVerifier,
    MypyVerifier,
    PytestVerifier,
    VerificationContext,
    VerificationManager,
)
from .sanitizers import Sanitizer, FunctionBodySanitizer, apply_sanitizers

__all__ = [
    "FunctionPlot",
    "extract_plots",
    "ContextItem",
    "PlotContext",
    "ContextGatherer",
    "ModuleContextGatherer",
    "ImportContextGatherer",
    "DependencyContextGatherer",
    "create_plot_source",
    "VerificationResult",
    "PlotVerifier",
    "ModuleVerifier",
    "MypyVerifier",
    "PytestVerifier",
    "VerificationContext",
    "VerificationManager",
    "Sanitizer",
    "FunctionBodySanitizer",
    "apply_sanitizers",
]
