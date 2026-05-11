from __future__ import annotations

from typing import Any, Mapping

from app.domain.osint_module import ConfidenceLevel, Finding, OsintModule, OsintResult
from infrastructure.plugins._http import get_json, with_query


class IntelXPlugin(OsintModule):
    name = "intelx"
    description = "Queries Intelligence X for leak/search indicators."
    required_inputs = set()
    optional_inputs = {"email", "phone"}
    required_env = {"INTELX_API_KEY"}
    base_url = "https://2.intelx.io/intelligent/search/result"

    def can_run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> tuple[bool, list[str]]:
        ok, missing = super().can_run(inputs, env)
        if not (inputs.get("email") or inputs.get("phone")):
            missing.append("email or phone")
        return ok and not missing, missing

    async def run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> OsintResult:
        env = env or {}
        selector = str(inputs.get("email") or inputs.get("phone"))
        result = OsintResult(module=self.name, ok=True)
        try:
            data = await get_json(
                with_query(self.base_url, {"term": selector, "maxresults": int(inputs.get("intelx_limit", 20))}),
                headers={"x-key": env["INTELX_API_KEY"]},
            )
            for record in data.get("records", []):
                result.findings.append(
                    Finding(
                        module=self.name,
                        type="leak_reference",
                        value=selector,
                        confidence=ConfidenceLevel.MEDIUM,
                        source=record.get("name") or record.get("bucket"),
                        metadata={"systemid": record.get("systemid"), "date": record.get("date"), "media": record.get("media")},
                    )
                )
        except Exception as exc:
            result.ok = False
            result.errors.append(str(exc))
        return result.finish()
