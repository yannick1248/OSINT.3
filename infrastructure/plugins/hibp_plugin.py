from __future__ import annotations

from typing import Any, Mapping

from app.domain.osint_module import ConfidenceLevel, Finding, OsintModule, OsintResult
from infrastructure.plugins._http import HttpError, get_json


class HibpPlugin(OsintModule):
    name = "hibp"
    description = "Queries Have I Been Pwned breach metadata for an email address."
    required_inputs = {"email"}
    required_env = {"HIBP_API_KEY"}

    async def run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> OsintResult:
        env = env or {}
        email = str(inputs["email"]).strip()
        result = OsintResult(module=self.name, ok=True)
        try:
            breaches = await get_json(
                f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false",
                headers={"hibp-api-key": env["HIBP_API_KEY"]},
            )
            for breach in breaches:
                result.findings.append(
                    Finding(
                        module=self.name,
                        type="breach",
                        value=email,
                        confidence=ConfidenceLevel.VERIFIED,
                        source=breach.get("Name"),
                        url=breach.get("Domain"),
                        metadata={"breach_date": breach.get("BreachDate"), "data_classes": breach.get("DataClasses", [])},
                    )
                )
        except HttpError as exc:
            if "HTTP 404" in str(exc):
                result.metadata["breaches"] = 0
            else:
                result.ok = False
                result.errors.append(str(exc))
        except Exception as exc:
            result.ok = False
            result.errors.append(str(exc))
        return result.finish()
