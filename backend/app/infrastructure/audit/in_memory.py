from __future__ import annotations

from app.domain.audit import AuditEvent


class InMemoryAuditSink:
    """Implémentation transitoire — à remplacer par un sink PostgreSQL."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    async def record(self, event: AuditEvent) -> None:
        self.events.append(event)
