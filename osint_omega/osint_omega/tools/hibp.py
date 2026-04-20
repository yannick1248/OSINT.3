"""Have I Been Pwned — vérification de compromission d'email."""

from __future__ import annotations

import os
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

HIBP_URL = "https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
HTTP_TIMEOUT = 10.0


class HIBPTool(Tool):
    name: ClassVar[str] = "hibp"
    description: ClassVar[str] = (
        "Have I Been Pwned — vérifie si un email apparaît dans des fuites."
    )
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.EMAIL})

    def __init__(
        self,
        *,
        api_key: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = api_key
        self._client = client

    def _resolve_api_key(self) -> str | None:
        return self._api_key or os.environ.get("HIBP_API_KEY")

    async def run(self, target: Target) -> ToolResult:
        started = time.perf_counter()
        api_key = self._resolve_api_key()
        if not api_key:
            return self._build_result(
                source=self.name,
                status=ToolStatus.SKIPPED,
                confidence=Confidence.LOW,
                started=started,
                error="HIBP_API_KEY non configurée.",
            )
        headers = {
            "hibp-api-key": api_key,
            "user-agent": "osint-omega/0.1",
        }
        url = HIBP_URL.format(email=target.value)
        try:
            client = self._client or httpx.AsyncClient(timeout=HTTP_TIMEOUT)
            owns_client = self._client is None
            try:
                resp = await client.get(url, headers=headers)
            finally:
                if owns_client:
                    await client.aclose()
        except httpx.HTTPError as exc:
            return self._build_result(
                source=self.name,
                status=ToolStatus.FAILED,
                confidence=Confidence.LOW,
                started=started,
                error=f"HIBP HTTP error: {exc}",
            )

        if resp.status_code == 404:
            return self._build_result(
                source=self.name,
                status=ToolStatus.SUCCESS,
                confidence=Confidence.HIGH,
                started=started,
                data={"email": target.value, "breaches": [], "breach_count": 0},
            )
        if resp.status_code != 200:
            return self._build_result(
                source=self.name,
                status=ToolStatus.FAILED,
                confidence=Confidence.LOW,
                started=started,
                error=f"HIBP unexpected status: {resp.status_code}",
            )

        breaches = resp.json()
        return self._build_result(
            source=self.name,
            status=ToolStatus.SUCCESS,
            confidence=Confidence.VERY_HIGH,
            started=started,
            data={
                "email": target.value,
                "breaches": [b.get("Name") for b in breaches if isinstance(b, dict)],
                "breach_count": len(breaches),
            },
        )
