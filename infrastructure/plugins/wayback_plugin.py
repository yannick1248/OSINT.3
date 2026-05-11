from __future__ import annotations

from typing import Any, Mapping

from app.domain.osint_module import ConfidenceLevel, Finding, OsintModule, OsintResult
from infrastructure.plugins._http import get_json, with_query


class WaybackPlugin(OsintModule):
    name = "wayback"
    description = "Collects archived URL evidence from the Internet Archive CDX API."
    required_inputs = {"domain"}

    async def run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> OsintResult:
        result = OsintResult(module=self.name, ok=True)
        domain = str(inputs["domain"]).strip()
        limit = int(inputs.get("wayback_limit", 50))
        try:
            rows = await get_json(
                with_query(
                    "https://web.archive.org/cdx",
                    {"url": f"*.{domain}/*", "output": "json", "fl": "timestamp,original,statuscode,mimetype", "collapse": "urlkey", "limit": limit},
                )
            )
            for row in rows[1:] if rows else []:
                timestamp, original, statuscode, mimetype = row
                result.findings.append(
                    Finding(
                        module=self.name,
                        type="archived_url",
                        value=original,
                        confidence=ConfidenceLevel.MEDIUM,
                        source="Internet Archive CDX",
                        url=f"https://web.archive.org/web/{timestamp}/{original}",
                        metadata={"timestamp": timestamp, "statuscode": statuscode, "mimetype": mimetype},
                    )
                )
        except Exception as exc:
            result.ok = False
            result.errors.append(str(exc))
        return result.finish()
