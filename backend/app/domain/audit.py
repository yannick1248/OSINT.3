from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.domain.scope import Scope


class AuditEvent(BaseModel):
    """Événement journalisé pour chaque action d'investigation.

    Alimente l'audit trail (exigence éthique/légale du projet) : qui a
    exécuté quel module, avec quels paramètres, à quel instant.
    """

    model_config = ConfigDict(frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor_id: str
    scope: Scope = Scope.SANDBOX_TEST
    module: str
    params: dict[str, Any]
    result_id: UUID | None = None
    outcome: str
