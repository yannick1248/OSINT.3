"""CRT.sh — énumération de sous-domaines via transparence de certificats."""

from __future__ import annotations

import time
from typing import ClassVar

import httpx

from osint_omega.tools.base import Tool
from osint_omega.types import (
    Confidence,
    Target,
    TargetType,
    ToolResult,
    ToolStatus,
)

CRTSH_URL = "https://crt.sh/"
HTTP_TIMEOUT = 15.0


class CrtShTool(Tool):
    name: ClassVar[str] = "crtsh"
    description: ClassVar[str] = (
        "Énumération de sous-domaines via crt.sh (transparence de certificats)."
    )
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.DOMAIN})

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def run(self, target: Target) -> ToolResult:
        started = time.perf_counter()
        params = {"q": f"%.{target.value}", "output": "json"}
        try:
            client = self._client or httpx.AsyncClient(timeout=HTTP_TIMEOUT)
            owns_client = self._client is None
            try:
                resp = await client.get(CRTSH_URL, params=params)
                resp.raise_for_status()
                payload = resp.json()
            finally:
                if owns_client:
                    await client.aclose()
        except httpx.HTTPError as exc:
            return self._build_result(
                source=self.name,
                status=ToolStatus.FAILED,
                confidence=Confidence.LOW,
                started=started,
                error=f"crt.sh HTTP error: {exc}",
            )

        names: set[str] = set()
        for entry in payload:
            for raw in (entry.get("name_value") or "").splitlines():
                name = raw.strip().lower().lstrip("*.")
                if name:
                    names.add(name)

        return self._build_result(
            source=self.name,
            status=ToolStatus.SUCCESS,
            confidence=Confidence.HIGH if names else Confidence.LOW,
            started=started,
            data={
                "domain": target.value,
                "subdomains": sorted(names),
                "count": len(names),
            },
        )
