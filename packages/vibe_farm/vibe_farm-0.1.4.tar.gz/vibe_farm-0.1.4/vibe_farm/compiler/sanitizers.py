# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
from __future__ import annotations
from vibe_farm.__about__ import __license__, __copyright__

"""Utilities for sanitizing LLM generated code before application."""

import ast
from typing import Protocol, Sequence


class Sanitizer(Protocol):
    """Protocol for sanitizer implementations."""

    def sanitize(self, code: str) -> str:
        """Return sanitized *code*."""
        ...  # pragma: no cover


class FunctionBodySanitizer:
    """Extract the body statements from a function definition if present."""

    def sanitize(self, code: str) -> str:
        try:
            module = ast.parse(code)
        except SyntaxError:
            return code

        if len(module.body) != 1:
            return code

        func = module.body[0]
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return code

        body = func.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body = body[1:]

        return "\n".join(ast.unparse(stmt) for stmt in body)


def apply_sanitizers(code: str, sanitizers: Sequence[Sanitizer]) -> str:
    """Return *code* after applying all *sanitizers* in sequence."""
    for sanitizer in sanitizers:
        code = sanitizer.sanitize(code)
    return code


__all__ = ["Sanitizer", "FunctionBodySanitizer", "apply_sanitizers"]
