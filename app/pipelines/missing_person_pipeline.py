"""Missing-person OSINT orchestration pipeline.

The pipeline enforces two non-negotiable audit fields before any plugin is run:
``legal_basis`` and ``requestor_id``.  This keeps operational use accountable while
allowing plugins to execute concurrently and independently.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from app.domain.osint_module import Finding, OsintModule, OsintResult
from infrastructure.plugins import (
    AhmiaPlugin,
    EyeOfWebPlugin,
    HibpPlugin,
    HolehePlugin,
    InsightFacePlugin,
    IntelXPlugin,
    TelegramPlugin,
    WaybackPlugin,
    WhatsMyNamePlugin,
)


@dataclass(slots=True)
class AuditEvent:
    event: str
    requestor_id: str
    legal_basis: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event,
            "requestor_id": self.requestor_id,
            "legal_basis": self.legal_basis,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class EntityCard:
    entity_id: str
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    username: str | None = None
    domain: str | None = None
    image_path: str | None = None
    finding_count: int = 0
    sources: list[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "username": self.username,
            "domain": self.domain,
            "image_path": self.image_path,
            "finding_count": self.finding_count,
            "sources": self.sources,
            "generated_at": self.generated_at.isoformat(),
        }


class MissingPersonPipeline:
    """Concurrent orchestrator for all available missing-person OSINT modules."""

    def __init__(self, modules: list[OsintModule] | None = None, env: Mapping[str, str] | None = None) -> None:
        self.modules = modules or [
            WhatsMyNamePlugin(),
            HolehePlugin(),
            IntelXPlugin(),
            HibpPlugin(),
            TelegramPlugin(),
            InsightFacePlugin(),
            EyeOfWebPlugin(),
            WaybackPlugin(),
            AhmiaPlugin(),
        ]
        self.env = dict(env or os.environ)

    async def investigate(self, inputs: Mapping[str, Any]) -> dict[str, Any]:
        legal_basis = str(inputs.get("legal_basis") or "").strip()
        requestor_id = str(inputs.get("requestor_id") or "").strip()
        if not legal_basis or not requestor_id:
            raise ValueError("legal_basis and requestor_id are mandatory")

        investigation_id = str(inputs.get("investigation_id") or uuid4())
        audit_trail = [
            AuditEvent(
                event="investigation_started",
                requestor_id=requestor_id,
                legal_basis=legal_basis,
                metadata={"investigation_id": investigation_id, "input_keys": sorted(inputs.keys())},
            )
        ]

        async def execute(module: OsintModule) -> OsintResult:
            can_run, missing = module.can_run(inputs, self.env)
            if not can_run:
                return module.skipped(missing)
            return await module.run(inputs, self.env)

        results = await asyncio.gather(*(execute(module) for module in self.modules), return_exceptions=True)
        normalized: list[OsintResult] = []
        for module, item in zip(self.modules, results, strict=True):
            if isinstance(item, Exception):
                normalized.append(OsintResult(module=module.name, ok=False, errors=[str(item)]).finish())
            else:
                normalized.append(item)

        findings = [finding for result in normalized for finding in result.findings]
        entity = self._entity_card(investigation_id, inputs, findings)
        audit_trail.append(
            AuditEvent(
                event="investigation_completed",
                requestor_id=requestor_id,
                legal_basis=legal_basis,
                metadata={"investigation_id": investigation_id, "finding_count": len(findings)},
            )
        )

        return {
            "investigation_id": investigation_id,
            "entity": entity.to_dict(),
            "results": [result.to_dict() for result in normalized],
            "findings": [finding.to_dict() for finding in findings],
            "audit_trail": [event.to_dict() for event in audit_trail],
        }

    @staticmethod
    def _entity_card(investigation_id: str, inputs: Mapping[str, Any], findings: list[Finding]) -> EntityCard:
        return EntityCard(
            entity_id=investigation_id,
            name=inputs.get("name"),
            email=inputs.get("email"),
            phone=inputs.get("phone"),
            username=inputs.get("username"),
            domain=inputs.get("domain"),
            image_path=inputs.get("image_path"),
            finding_count=len(findings),
            sources=sorted({finding.module for finding in findings}),
        )
