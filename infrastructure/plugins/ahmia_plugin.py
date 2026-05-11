from __future__ import annotations

import re
from html import unescape
from typing import Any, Mapping
from urllib.parse import quote_plus

from app.domain.osint_module import ConfidenceLevel, Finding, OsintModule, OsintResult
from infrastructure.plugins._http import get_text


class AhmiaPlugin(OsintModule):
    name = "ahmia"
    description = "Searches Ahmia for dark-web references to a person or contact indicator."
    required_inputs = set()
    optional_inputs = {"name", "email"}

    def can_run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> tuple[bool, list[str]]:
        if inputs.get("name") or inputs.get("email"):
            return True, []
        return False, ["name or email"]

    async def run(self, inputs: Mapping[str, Any], env: Mapping[str, str] | None = None) -> OsintResult:
        query = str(inputs.get("email") or inputs.get("name"))
        result = OsintResult(module=self.name, ok=True)
        try:
            html = await get_text(f"https://ahmia.fi/search/?q={quote_plus(query)}")
            for href, title in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, flags=re.I | re.S)[: int(inputs.get("ahmia_limit", 25))]:
                clean_title = re.sub(r"<[^>]+>", " ", title)
                clean_title = " ".join(unescape(clean_title).split())
                if clean_title:
                    result.findings.append(
                        Finding(
                            module=self.name,
                            type="darkweb_reference",
                            value=query,
                            confidence=ConfidenceLevel.LOW,
                            source="Ahmia",
                            url=href,
                            metadata={"title": clean_title},
                        )
                    )
        except Exception as exc:
            result.ok = False
            result.errors.append(str(exc))
        return result.finish()
