# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
from __future__ import annotations

from vibe_farm.__about__ import __license__, __copyright__

"""Verification strategies for generated code."""

import ast
import logging
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

from .plots import FunctionPlot


@dataclass
class VerificationResult:
    """Result of a verification operation."""

    success: bool
    message: str
    details: str = ""

    def __str__(self) -> str:
        """Return a string representation of the verification result."""
        if self.success:
            return f"✓ {self.message}"
        return (
            f"✗ {self.message}\n{self.details}" if self.details else f"✗ {self.message}"
        )


@runtime_checkable
class PlotVerifier(Protocol):
    """Protocol for plot-level verification strategies."""

    name: str

    def verify_plot(
        self, plot: FunctionPlot, generated_code: str
    ) -> VerificationResult:
        """Verify a single plot with generated code.

        Args:
            plot: The function plot being verified
            generated_code: The generated code for the plot

        Returns:
            VerificationResult indicating success or failure
        """
        ...


@runtime_checkable
class ModuleVerifier(Protocol):
    """Protocol for module-level verification strategies."""

    name: str

    def verify_module(
        self, module_path: Path, module_ast: ast.Module
    ) -> VerificationResult:
        """Verify a complete module after all plots have been filled.

        Args:
            module_path: Path to the module being verified
            module_ast: The AST of the module with filled plots

        Returns:
            VerificationResult indicating success or failure
        """
        ...


class MypyVerifier:
    """Verifier that uses mypy to type check generated code."""

    name = "mypy"

    def verify_plot(
        self, plot: FunctionPlot, generated_code: str
    ) -> VerificationResult:
        """Verify a plot by type checking the generated code in context."""
        # For plot-level verification, we'll create a temporary module
        # with the complete function signature and generated body
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                # Write a complete function with the generated code
                f.write(f"# Generated code for {plot.qualname}\n")
                f.write(ast.unparse(plot.node))
                f.flush()

                temp_path = Path(f.name)

            # Run mypy on the temporary file
            result = subprocess.run(
                ["mypy", "--no-error-summary", str(temp_path)],
                capture_output=True,
                text=True,
            )

            # Clean up
            temp_path.unlink()

            if result.returncode == 0:
                return VerificationResult(
                    success=True, message=f"Type checking passed for {plot.qualname}"
                )
            else:
                return VerificationResult(
                    success=False,
                    message=f"Type checking failed for {plot.qualname}",
                    details=result.stdout,
                )

        except Exception as e:
            return VerificationResult(
                success=False,
                message=f"Type checking error for {plot.qualname}",
                details=str(e),
            )

    def verify_module(
        self, module_path: Path, module_ast: ast.Module
    ) -> VerificationResult:
        """Verify a complete module using mypy."""
        try:
            # Write the module AST to a temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(ast.unparse(module_ast))
                f.flush()
                temp_path = Path(f.name)

            # Run mypy on the temporary file
            result = subprocess.run(
                ["mypy", "--no-error-summary", str(temp_path)],
                capture_output=True,
                text=True,
            )

            # Clean up
            temp_path.unlink()

            if result.returncode == 0:
                return VerificationResult(
                    success=True,
                    message=f"Module type checking passed for {module_path}",
                )
            else:
                return VerificationResult(
                    success=False,
                    message=f"Module type checking failed for {module_path}",
                    details=result.stdout,
                )

        except Exception as e:
            return VerificationResult(
                success=False,
                message=f"Module type checking error for {module_path}",
                details=str(e),
            )


class PytestVerifier:
    """Verifier that executes pytest tests for a module."""

    name = "pytest"

    def verify_module(
        self, module_path: Path, module_ast: ast.Module
    ) -> VerificationResult:
        """Run pytest on a companion ``*_test.py`` file if present."""
        test_file = module_path.with_name(module_path.stem + "_test.py")

        if not test_file.exists():
            return VerificationResult(
                success=True,
                message=f"No tests found for {module_path}, skipping pytest",
            )

        vibe_file = module_path.with_suffix(".vibe.py")
        original_contents = vibe_file.read_text() if vibe_file.exists() else None

        try:
            vibe_file.write_text(ast.unparse(module_ast))

            result = subprocess.run(
                ["pytest", str(test_file)], capture_output=True, text=True
            )

            if result.returncode == 0:
                return VerificationResult(
                    success=True, message=f"Pytest passed for {module_path}"
                )
            return VerificationResult(
                success=False,
                message=f"Pytest failed for {module_path}",
                details=result.stdout,
            )
        except Exception as e:
            return VerificationResult(
                success=False,
                message=f"Pytest error for {module_path}",
                details=str(e),
            )
        finally:
            if original_contents is not None:
                vibe_file.write_text(
                    original_contents
                )  # pragma: no cover - restoration path
            else:
                vibe_file.unlink(missing_ok=True)


@dataclass
class VerificationContext:
    """Context for verification operations, including retry history."""

    plot: FunctionPlot | None = None
    module_path: Path | None = None
    attempt_count: int = 0
    previous_failures: list[VerificationResult] = field(default_factory=list)

    def add_failure(self, result: VerificationResult) -> None:
        """Add a failed verification result to the context."""
        self.previous_failures.append(result)
        self.attempt_count += 1

    def get_failure_context(self) -> str:
        """Get a formatted string of all previous failures for LLM context."""
        if not self.previous_failures:
            return ""

        context_parts = ["Previous verification failures:"]
        for i, failure in enumerate(self.previous_failures, 1):
            context_parts.append(f"Attempt {i}: {failure.message}")
            if failure.details:
                context_parts.append(f"Details: {failure.details}")

        return "\n".join(context_parts)


class VerificationManager:
    """Manages verification strategies and retry logic."""

    def __init__(
        self,
        plot_verifiers: list[PlotVerifier] | None = None,
        module_verifiers: list[ModuleVerifier] | None = None,
        max_retries: int = 2,
        logger: logging.Logger | None = None,
    ) -> None:
        self.plot_verifiers = plot_verifiers or []
        self.module_verifiers = module_verifiers or []
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)

    def verify_plot(
        self,
        plot: FunctionPlot,
        generated_code: str,
        context: VerificationContext | None = None,
    ) -> tuple[bool, VerificationContext]:
        """Verify a plot using all configured plot verifiers.

        Returns:
            Tuple of (success, verification_context)
        """
        if context is None:
            context = VerificationContext(plot=plot)

        all_successful = True
        for verifier in self.plot_verifiers:
            self.logger.info(
                f"Running {verifier.name} verification for {plot.qualname}"
            )
            result = verifier.verify_plot(plot, generated_code)

            if not result.success:
                all_successful = False
                context.add_failure(result)
                self.logger.warning(f"Verification failed: {result}")
            else:
                self.logger.info(f"Verification passed: {result}")

        return all_successful, context

    def verify_module(
        self,
        module_path: Path,
        module_ast: ast.Module,
        context: VerificationContext | None = None,
    ) -> tuple[bool, VerificationContext]:
        """Verify a module using all configured module verifiers.

        Returns:
            Tuple of (success, verification_context)
        """
        if context is None:
            context = VerificationContext(module_path=module_path)

        all_successful = True
        for verifier in self.module_verifiers:
            self.logger.info(f"Running {verifier.name} verification for {module_path}")
            result = verifier.verify_module(module_path, module_ast)

            if not result.success:
                all_successful = False
                context.add_failure(result)
                self.logger.warning(f"Verification failed: {result}")
            else:
                self.logger.info(f"Verification passed: {result}")

        return all_successful, context

    def should_retry(self, context: VerificationContext) -> bool:
        """Determine if we should retry based on the context."""
        return context.attempt_count < self.max_retries


__all__ = [
    "VerificationResult",
    "PlotVerifier",
    "ModuleVerifier",
    "MypyVerifier",
    "PytestVerifier",
    "VerificationContext",
    "VerificationManager",
]
