# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
from vibe_farm.__about__ import __license__, __copyright__

"""
Entry point for the vibe_farm compiler CLI.
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from .compiler import providers

load_dotenv()


def main() -> None:
    """Run the ``vibe_farm`` command line interface.

    Parses command line arguments and executes the requested command.

    Returns:
        ``None``. Exits the program via :class:`SystemExit` on error.
    """
    # Check if first argument looks like a command or a file/directory

    # Handle backward compatibility: if first arg is not a known command,
    # treat it as a file for the compile command
    if len(sys.argv) > 1 and sys.argv[1] not in ["compile", "analyze"]:
        # Old format: vibe_farm <sources...>
        parser = argparse.ArgumentParser(
            prog="vibe_farm",
            description="vibe_farm compiler: Compile Vibe source files.",
        )
        parser.add_argument(
            "sources",
            nargs="+",
            type=Path,
            help="Path(s) to Vibe source file(s) or directories to compile.",
        )
        parser.add_argument(
            "--provider",
            choices=providers.PROVIDER_NAMES,
            help="LLM provider for code generation",
        )
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Recompile existing plots",
        )
        parser.add_argument(
            "--log-level",
            choices=["info", "warning", "error"],
            default="warning",
            help="Logging verbosity",
        )
        parser.add_argument(
            "--max-retries",
            type=int,
            default=2,
            help="Maximum number of retries for verification failures",
        )
        parser.add_argument(
            "--enable-verification",
            action="store_true",
            help="Enable verification of generated code",
        )
        args = parser.parse_args()
        command = "compile"
        sources = args.sources
        provider_name = getattr(args, "provider", None)
        force = args.force
        log_level = args.log_level
        max_retries = getattr(args, "max_retries", 2)
        enable_verification = getattr(args, "enable_verification", False)
    else:
        # New format: vibe_farm <command> <sources...>
        parser = argparse.ArgumentParser(
            prog="vibe_farm",
            description="vibe_farm: A tool for compiling and analyzing Vibe source files.",
        )

        # Create subparsers for different commands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        subparsers.required = True

        # Compile command (default behavior)
        compile_parser = subparsers.add_parser(
            "compile", help="Compile Vibe source files"
        )
        compile_parser.add_argument(
            "sources",
            nargs="+",
            type=Path,
            help="Path(s) to Vibe source file(s) or directories to compile.",
        )
        compile_parser.add_argument(
            "--provider",
            choices=providers.PROVIDER_NAMES,
            help="LLM provider for code generation",
        )
        compile_parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Recompile existing plots",
        )
        compile_parser.add_argument(
            "--log-level",
            choices=["info", "warning", "error"],
            default="warning",
            help="Logging verbosity",
        )
        compile_parser.add_argument(
            "--max-retries",
            type=int,
            default=2,
            help="Maximum number of retries for verification failures",
        )
        compile_parser.add_argument(
            "--enable-verification",
            action="store_true",
            help="Enable verification of generated code",
        )

        # Analyze command
        analyze_parser = subparsers.add_parser(
            "analyze", help="Analyze Vibe source files for raise code() statements"
        )
        analyze_parser.add_argument(
            "sources",
            nargs="+",
            type=Path,
            help="Path(s) to Vibe source file(s) or directories to analyze.",
        )
        analyze_parser.add_argument(
            "--log-level",
            choices=["info", "warning", "error"],
            default="warning",
            help="Logging verbosity",
        )

        args = parser.parse_args()
        command = args.command
        sources = args.sources
        provider_name = getattr(args, "provider", None)
        force = getattr(args, "force", False)
        log_level = args.log_level
        max_retries = getattr(args, "max_retries", 2)
        enable_verification = getattr(args, "enable_verification", False)

    # Execute the appropriate command
    if command == "compile":
        from .commands.compile import compile_command

        compile_command(
            sources,
            provider_name,
            force=force,
            log_level=log_level,
            max_retries=max_retries,
            enable_verification=enable_verification,
        )
    elif command == "analyze":
        from .commands.analyze import analyze_command

        analyze_command(sources)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# No typing generics to update in this file.
