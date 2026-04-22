"""Types de base partagés par tous les modules osint_omega."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TargetType(str, Enum):
    USERNAME = "username"
    EMAIL = "email"
    DOMAIN = "domain"
    IP = "ip"
    PERSON = "person"
    COMPANY = "company"
    ONION = "onion"
    FREE_TEXT = "free_text"


class Scope(str, Enum):
    """Périmètres de mission (modèle Perplexity multi-agent)."""

    SANDBOX_TEST = "SANDBOX_TEST"
    OWNED_ASSETS = "OWNED_ASSETS"
    CLIENT_AUTHORIZED_SCOPE = "CLIENT_AUTHORIZED_SCOPE"
    PUBLIC_INTEREST_RESEARCH = "PUBLIC_INTEREST_RESEARCH"
    INTERNAL_AUDIT = "INTERNAL_AUDIT"
    LEGALLY_RESTRICTED = "LEGALLY_RESTRICTED"


class Confidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class ToolStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    TOOL_NOT_INSTALLED = "TOOL_NOT_INSTALLED"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class Target(BaseModel):
    """Cible d'une mission d'investigation."""

    model_config = ConfigDict(frozen=True)

    value: str = Field(..., min_length=1, max_length=512)
    type: TargetType

    @field_validator("value")
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()


class ToolResult(BaseModel):
    """Résultat normalisé produit par chaque wrapper d'outil."""

    model_config = ConfigDict(frozen=True)

    source: str
    status: ToolStatus
    confidence: Confidence
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    cache_hit: bool = False


class Mission(BaseModel):
    """Mission = cible + périmètre + résultats agrégés."""

    model_config = ConfigDict(frozen=True)

    mission_id: UUID = Field(default_factory=uuid4)
    target: Target
    scope: Scope
    actor_id: str = "anonymous"
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    results: list[ToolResult] = Field(default_factory=list)
    gate_notes: list[str] = Field(default_factory=list)

    @property
    def aggregated_confidence(self) -> Confidence:
        """Confiance agrégée basée sur la corroboration multi-sources."""
        successes = [r for r in self.results if r.status == ToolStatus.SUCCESS]
        if not successes:
            return Confidence.LOW
        levels = {c: i for i, c in enumerate(Confidence)}
        avg = sum(levels[r.confidence] for r in successes) / len(successes)
        corroboration_bonus = 1 if len(successes) >= 3 else 0
        idx = min(len(Confidence) - 1, int(round(avg)) + corroboration_bonus)
        return list(Confidence)[idx]
