from __future__ import annotations

from typing import Protocol

from app.domain.audit import AuditEvent


class AuditSink(Protocol):
    """Port de sortie pour persister les événements d'audit."""

    async def record(self, event: AuditEvent) -> None: ...
