from __future__ import annotations

"""Configuration context for command execution."""

from dataclasses import dataclass, field
import logging
from logging import Logger
from ..compiler import providers
from ..compiler.verification import VerificationManager
from ..compiler.sanitizers import Sanitizer, FunctionBodySanitizer


@dataclass
class CompileContext:
    """Context information for compilation commands."""

    provider: providers.LLMProvider | None
    verification_manager: VerificationManager | None = None
    sanitizers: list[Sanitizer] = field(
        default_factory=lambda: [FunctionBodySanitizer()]
    )
    force: bool = False
    max_retries: int = 2
    logger: Logger = logging.getLogger("vibe_farm")


__all__ = ["CompileContext"]
