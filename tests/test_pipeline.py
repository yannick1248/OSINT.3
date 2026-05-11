from __future__ import annotations

import asyncio
from typing import Any, Mapping

from app.domain.osint_module import ConfidenceLevel, Finding, OsintModule, OsintResult
from app.pipelines.missing_person_pipeline import MissingPersonPipeline


class StaticModule(OsintModule):
    name = "static"
    required_inputs = {"email"}

    async def run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> OsintResult:
        return OsintResult(
            module=self.name,
            ok=True,
            findings=[Finding(module=self.name, type="email", value=str(inputs["email"]), confidence=ConfidenceLevel.HIGH)],
        ).finish()


def test_pipeline_requires_audit_fields() -> None:
    pipeline = MissingPersonPipeline(modules=[StaticModule()], env={})
    try:
        asyncio.run(pipeline.investigate({"email": "jane@example.org"}))
    except ValueError as exc:
        assert "legal_basis" in str(exc)
    else:
        raise AssertionError("pipeline accepted unaudited request")


def test_pipeline_generates_entity_and_audit_trail() -> None:
    pipeline = MissingPersonPipeline(modules=[StaticModule()], env={})
    report = asyncio.run(
        pipeline.investigate(
            {
                "requestor_id": "unit-test",
                "legal_basis": "test-case",
                "email": "jane@example.org",
            }
        )
    )
    assert report["entity"]["finding_count"] == 1
    assert report["entity"]["sources"] == ["static"]
    assert [event["event"] for event in report["audit_trail"]] == ["investigation_started", "investigation_completed"]
