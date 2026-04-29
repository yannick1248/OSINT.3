"""Interface commune à tous les wrappers d'outils."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import ClassVar

from osint_omega.types import (
    Confidence,
    Target,
    TargetType,
    ToolResult,
    ToolStatus,
)


class Tool(ABC):
    """Un wrapper implémente ``run`` et déclare ses types de cibles supportés."""

    name: ClassVar[str]
    description: ClassVar[str]
    supported_targets: ClassVar[frozenset[TargetType]]

    def supports(self, target_type: TargetType) -> bool:
        return target_type in self.supported_targets

    @abstractmethod
    async def run(self, target: Target) -> ToolResult: ...

    def cache_key(self, target: Target) -> str:
        return f"{self.name}:{target.type.value}:{target.value.lower()}"

    @staticmethod
    def _build_result(
        *,
        source: str,
        status: ToolStatus,
        confidence: Confidence,
        started: float,
        data: dict | None = None,
        error: str | None = None,
    ) -> ToolResult:
        duration_ms = int((time.perf_counter() - started) * 1000)
        return ToolResult(
            source=source,
            status=status,
            confidence=confidence,
            duration_ms=duration_ms,
            data=data or {},
            error=error,
        )
