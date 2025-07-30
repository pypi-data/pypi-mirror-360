# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
from __future__ import annotations
from vibe_farm.__about__ import __license__, __copyright__

"""Prompt generation utilities for LLM-driven compilation."""

from .context import PlotContext
from .verification import VerificationContext


def create_prompt(
    context: PlotContext, verification_context: VerificationContext | None = None
) -> str:
    """Return a prompt requesting implementation for ``context.plot``."""
    lines = [
        f"""
        Implement the Python function/method {context.plot.qualname} using the following context.
        Respond with valid Python source code only: no narrative or surrounding explanation. 
        Do not respond with markdown formatting or any format fencing, only respond with code.
        Do not respond with the function/method signature or docstring, only the body statements because our tool will take your statements and plug them into the definition.
        Do not indent the statements unless they are in nested blocks, we will handle indentation of the top-level statements.
        """.strip(),
    ]

    # Add verification failure context if available
    if verification_context and verification_context.previous_failures:
        lines.append("")
        lines.append("# Previous implementation attempts failed verification:")
        lines.append(verification_context.get_failure_context())
        lines.append("# Please address the above issues in your implementation.")

    for item in context.items:
        lines.append(f"# From {item.path}:{item.start_line}-{item.end_line}")
        lines.append(item.source)
    lines.append("# Implementation:")
    return "\n".join(lines)


__all__ = ["create_prompt"]
