# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
"""CLI command for compiling Vibe source files."""

from __future__ import annotations
from vibe_farm.__about__ import __license__, __copyright__

from pathlib import Path
import ast
import sys
import logging

from .utils import gather_python_sources, post_process_vibe_files
from .context import CompileContext
from .. import dependencies as dep_utils
from ..analysis import ast_utils
from ..compiler import (
    FunctionPlot,
    PlotContext,
    ContextGatherer,
    ModuleContextGatherer,
    ImportContextGatherer,
    DependencyContextGatherer,
    extract_plots,
    ContextItem,
)
from ..compiler import providers, prompt
from ..compiler.plots import apply_generated_code
from ..compiler.sanitizers import apply_sanitizers


def compile_command(
    sources: list[Path],
    provider_name: str | None = None,
    *,
    force: bool = False,
    log_level: str = "warning",
    max_retries: int = 2,
    enable_verification: bool = False,
) -> None:
    """Compile the specified Vibe source files."""

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.WARNING),
        format="%(message)s",
        stream=sys.stdout,
        force=True,
    )

    provider = (
        providers.provider_from_name(provider_name)
        if provider_name
        else providers.auto_provider()
    )

    # Set up verification strategies if enabled
    verification_manager = None
    if enable_verification:
        from ..compiler.verification import (
            VerificationManager,
            MypyVerifier,
            PytestVerifier,
        )

        verification_manager = VerificationManager(
            plot_verifiers=[],
            module_verifiers=[MypyVerifier(), PytestVerifier()],
            max_retries=max_retries,
            logger=logging.getLogger("vibe_farm.verification"),
        )

    context = CompileContext(
        provider=provider,
        verification_manager=verification_manager,
        force=force,
        max_retries=max_retries,
        logger=logging.getLogger("vibe_farm"),
    )

    dep_file = dep_utils.find_dependency_file(Path.cwd())
    dep_list = dep_utils.parse_dependencies(dep_file) if dep_file else []
    dep_names = dep_utils.dependency_names(dep_list)

    _compile_sources(sources, context, dep_list, dep_names, dep_file)


def _compile_sources(
    sources: list[Path],
    context: CompileContext,
    dependencies: list[str],
    dep_names: set[str],
    dep_path: Path | None,
) -> None:
    expanded_sources = gather_python_sources(sources)

    if context.provider:
        context.logger.info(f"Using provider {context.provider.name}")

    gatherers: list[ContextGatherer] = [
        ModuleContextGatherer(),
        ImportContextGatherer(),
    ]
    if dependencies and dep_path:
        gatherers.append(
            DependencyContextGatherer(dependencies, dep_path)
        )  # pragma: no cover - simple branch

    vibe_files: list[Path] = []
    for src in expanded_sources:
        context.logger.info(f"Compiling {src}")

        module_source = src.read_text()
        module_ast = ast_utils.parse_python_file(src)
        plots = extract_plots(src, module_ast)

        if not plots:
            continue

        vibe_file = src.with_suffix(".vibe.py")
        vibe_ast = None
        if not context.force and vibe_file.exists():
            vibe_ast = ast_utils.parse_python_file(vibe_file)

        # Process each plot with verification and retry logic
        for plot in plots:
            if vibe_ast and _plot_is_up_to_date(plot, vibe_ast):
                continue

            # Generate code for this plot with retries
            if not _generate_plot_with_verification(
                plot,
                module_ast,
                module_source,
                gatherers,
                context,
                dep_names,
            ):
                context.logger.error(
                    f"Failed to generate valid code for {plot.qualname} after {context.max_retries} retries"
                )
                sys.exit(1)

        # After all plots are processed, perform module-level verification
        if context.verification_manager:
            from ..compiler.verification import VerificationContext

            module_context = VerificationContext(module_path=src)

            remove_vibefarm_imports(module_ast)

            # Verify the complete module
            success, module_context = context.verification_manager.verify_module(
                src, module_ast, module_context
            )

            retry_count = 0
            while not success and retry_count < context.max_retries:
                context.logger.info(
                    f"Module verification failed, retrying module compilation (attempt {retry_count + 1})"
                )

                # Re-parse the original module for retry
                module_ast = ast_utils.parse_python_file(src)

                # Regenerate all plots with module failure context
                for plot in plots:
                    contexts: list[ContextItem] = []
                    for gatherer in gatherers:
                        contexts.extend(
                            gatherer.gather(plot, module_ast, module_source)
                        )
                    plot_context = PlotContext(plot, contexts)

                    prompt_text = prompt.create_prompt(plot_context, module_context)
                    assert context.provider is not None
                    generated = context.provider.generate(prompt_text)
                    generated = apply_sanitizers(generated, context.sanitizers)
                    dep_utils.warn_missing_imports(generated, dep_names, context.logger)
                    apply_generated_code(plot, generated)

                remove_vibefarm_imports(module_ast)
                success, module_context = context.verification_manager.verify_module(
                    src, module_ast, module_context
                )
                retry_count += 1

            if not success:
                context.logger.error(
                    f"Module verification failed for {src} after {context.max_retries} retries"
                )
                sys.exit(1)
        else:
            remove_vibefarm_imports(module_ast)

        new_source = ast.unparse(module_ast)
        vibe_file = src.with_suffix(".vibe.py")
        vibe_file.write_text(new_source)
        vibe_files.append(vibe_file)

    post_process_vibe_files(vibe_files)


def _generate_plot_with_verification(
    plot: FunctionPlot,
    module_ast: ast.Module,
    module_source: str,
    gatherers: list[ContextGatherer],
    context: CompileContext,
    available_dependencies: set[str],
) -> bool:
    """Generate code for a plot with verification and retry logic.

    Returns True if successful, False if all retries failed.
    """
    from ..compiler.verification import VerificationContext

    verification_context = VerificationContext(plot=plot)

    while True:
        # Gather context for this plot
        contexts: list[ContextItem] = []
        for gatherer in gatherers:
            contexts.extend(gatherer.gather(plot, module_ast, module_source))
        plot_context = PlotContext(plot, contexts)

        context.logger.info(f"Context for {plot.qualname}:")
        for item in plot_context.items:
            context.logger.info(f"{item.path}:{item.start_line}-{item.end_line}")
            context.logger.info(item.source)

        if context.provider is None:
            context.logger.error("Error: provider required for code generation")
            return False

        # Create prompt with verification failure context
        prompt_text = prompt.create_prompt(plot_context, verification_context)
        generated = context.provider.generate(prompt_text)
        dep_utils.warn_missing_imports(
            generated, available_dependencies, context.logger
        )

        generated = apply_sanitizers(generated, context.sanitizers)

        # Apply the generated code
        apply_generated_code(plot, generated)

        # Verify the generated code if verification manager is available
        if context.verification_manager:
            success, verification_context = context.verification_manager.verify_plot(
                plot, generated, verification_context
            )

            if success:
                return True

            # Check if we should retry
            if not context.verification_manager.should_retry(
                verification_context
            ):  # pragma: no cover - rare branch
                context.logger.error(
                    f"Plot verification failed for {plot.qualname} after {context.max_retries} attempts"
                )
                return False

            context.logger.info(
                f"Plot verification failed, retrying (attempt {verification_context.attempt_count + 1})"
            )  # pragma: no cover - hard to trigger in tests
            continue  # pragma: no cover - hard to trigger in tests
        else:
            # No verification, so we're done
            return True


def _plot_is_up_to_date(plot: FunctionPlot, vibe_ast: ast.Module) -> bool:
    node = _find_function(vibe_ast, plot.qualname)
    if node is None:
        return False
    for stmt in node.body:
        if (
            isinstance(stmt, ast.Raise)
            and isinstance(stmt.exc, ast.Call)
            and isinstance(stmt.exc.func, ast.Name)
            and stmt.exc.func.id == "code"
        ):
            return False
    return True


def _find_function(module: ast.Module, qualname: str) -> ast.FunctionDef | None:
    parts = qualname.split(".")
    body = module.body
    for part in parts[:-1]:
        cls = next(
            (n for n in body if isinstance(n, ast.ClassDef) and n.name == part),
            None,
        )
        if cls is None:
            return None
        body = cls.body
    for node in body:
        if isinstance(node, ast.FunctionDef) and node.name == parts[-1]:
            return node
    return None


def remove_vibefarm_imports(module_ast: ast.Module) -> None:
    """Remove farm and code imports from vibe_farm in *module_ast*."""

    new_body: list[ast.stmt] = []
    for stmt in module_ast.body:
        if isinstance(stmt, ast.ImportFrom) and stmt.module == "vibe_farm":
            stmt.names = [
                alias for alias in stmt.names if alias.name not in {"farm", "code"}
            ]
            if not stmt.names:
                continue
        new_body.append(stmt)
    module_ast.body = new_body


# Re-export internals for tests ------------------------------------------------

from ..compiler.plots import (
    create_plot_source,
    extract_plots as extract_plots_internal,
)  # noqa: E402

__all__ = [
    "compile_command",
    "FunctionPlot",
    "PlotContext",
    "ContextGatherer",
    "create_plot_source",
    "extract_plots_internal",
]
