"""Shared domain contracts for OSINT modules.

Every plugin returns normalized, auditable findings instead of leaking provider-specific
payloads into the application layer.  The contract is intentionally small so modules
can run offline or with self-hosted services when the investigation context requires it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, ClassVar, Mapping


class ConfidenceLevel(str, Enum):
    """Normalized confidence levels for findings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"


@dataclass(slots=True)
class Finding:
    """One normalized observation produced by an OSINT module."""

    module: str
    type: str
    value: str
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    source: str | None = None
    url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "type": self.type,
            "value": self.value,
            "confidence": self.confidence.value,
            "source": self.source,
            "url": self.url,
            "metadata": self.metadata,
            "discovered_at": self.discovered_at.isoformat(),
        }


@dataclass(slots=True)
class OsintResult:
    """Execution envelope for one OSINT module."""

    module: str
    ok: bool
    findings: list[Finding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def finish(self) -> "OsintResult":
        self.finished_at = datetime.now(timezone.utc)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "ok": self.ok,
            "findings": [finding.to_dict() for finding in self.findings],
            "errors": self.errors,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "metadata": self.metadata,
        }


class OsintModule(ABC):
    """Abstract base class implemented by every OSINT plugin."""

    name: ClassVar[str]
    description: ClassVar[str] = ""
    required_inputs: ClassVar[set[str]] = set()
    optional_inputs: ClassVar[set[str]] = set()
    required_env: ClassVar[set[str]] = set()

    def can_run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> tuple[bool, list[str]]:
        """Return whether the module has its required inputs and environment."""

        env = env or {}
        missing = [key for key in sorted(self.required_inputs) if not inputs.get(key)]
        missing.extend(key for key in sorted(self.required_env) if not env.get(key))
        return not missing, missing

    def skipped(self, missing: list[str]) -> OsintResult:
        """Create a standard skipped result for orchestration reports."""

        return OsintResult(
            module=self.name,
            ok=False,
            errors=[f"missing required value: {item}" for item in missing],
            metadata={"skipped": True},
        ).finish()

    @abstractmethod
    async def run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> OsintResult:
        """Execute the module and return normalized results."""
