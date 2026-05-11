from __future__ import annotations

from typing import Any, Mapping

from app.domain.osint_module import ConfidenceLevel, Finding, OsintModule, OsintResult
from infrastructure.plugins._http import get_json


class WhatsMyNamePlugin(OsintModule):
    name = "whatsmyname"
    description = "Checks a username against the WhatsMyName site catalogue."
    required_inputs = {"username"}
    wmndata_url = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmndata.json"

    async def run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> OsintResult:
        result = OsintResult(module=self.name, ok=True)
        username = str(inputs["username"]).strip()
        try:
            catalogue = await get_json(str(inputs.get("wmndata_url") or self.wmndata_url))
            for site in catalogue.get("sites", []):
                uri_check = site.get("uri_check") or site.get("uri_pretty")
                if not uri_check:
                    continue
                result.findings.append(
                    Finding(
                        module=self.name,
                        type="username_candidate",
                        value=username,
                        confidence=ConfidenceLevel.LOW,
                        source=site.get("name"),
                        url=str(uri_check).replace("{account}", username),
                        metadata={"category": site.get("cat"), "expected": site.get("e_code")},
                    )
                )
        except Exception as exc:  # provider/network failures should not stop the pipeline
            result.ok = False
            result.errors.append(str(exc))
        return result.finish()
