"""Analyse syntaxique locale d'un nom de domaine — toujours disponible."""

from __future__ import annotations

import re
import time
from typing import ClassVar

from osint_omega.tools.base import Tool
from osint_omega.types import (
    Confidence,
    Target,
    TargetType,
    ToolResult,
    ToolStatus,
)

_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(?:\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))+$"
)


class DomainSyntaxTool(Tool):
    name: ClassVar[str] = "domain_syntax"
    description: ClassVar[str] = "Analyse syntaxique locale d'un nom de domaine."
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.DOMAIN})

    async def run(self, target: Target) -> ToolResult:
        started = time.perf_counter()
        domain = target.value.lower()
        ok = bool(_DOMAIN_RE.match(domain))
        labels = domain.split(".") if ok else []
        return self._build_result(
            source=self.name,
            status=ToolStatus.SUCCESS if ok else ToolStatus.FAILED,
            confidence=Confidence.VERY_HIGH if ok else Confidence.LOW,
            started=started,
            data={
                "domain": domain,
                "is_well_formed": ok,
                "labels": labels,
                "tld": labels[-1] if labels else "",
            },
        )
