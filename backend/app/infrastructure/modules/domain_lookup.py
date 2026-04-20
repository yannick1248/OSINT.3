from __future__ import annotations

import re
import time
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator

from app.domain.modules.base import (
    ConfidenceLevel,
    OsintModule,
    OsintResult,
    OsintResultStatus,
)

_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(?:\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))+$"
)


class DomainLookupParams(BaseModel):
    domain: str = Field(..., min_length=3, max_length=253)

    @field_validator("domain")
    @classmethod
    def _normalize(cls, value: str) -> str:
        return value.strip().lower()


class DomainLookupOutput(BaseModel):
    domain: str
    is_well_formed: bool
    labels: list[str]
    tld: str


class DomainLookupModule(OsintModule[DomainLookupParams, DomainLookupOutput]):
    """Module d'exemple : analyse syntaxique d'un nom de domaine.

    Sert de référence pour la structure des modules. À remplacer/compléter
    par un vrai lookup WHOIS/DNS via un adaptateur réseau dédié.
    """

    name: ClassVar[str] = "domain_lookup"
    description: ClassVar[str] = "Analyse syntaxique basique d'un nom de domaine."
    input_schema: ClassVar[type[BaseModel]] = DomainLookupParams
    output_schema: ClassVar[type[BaseModel]] = DomainLookupOutput

    async def validate_input(self, params: DomainLookupParams) -> bool:
        return bool(_DOMAIN_RE.match(params.domain))

    async def execute(
        self, params: DomainLookupParams
    ) -> OsintResult[DomainLookupOutput]:
        start = time.perf_counter()
        is_well_formed = await self.validate_input(params)
        labels = params.domain.split(".") if is_well_formed else []
        output = DomainLookupOutput(
            domain=params.domain,
            is_well_formed=is_well_formed,
            labels=labels,
            tld=labels[-1] if labels else "",
        )
        return OsintResult[DomainLookupOutput](
            module=self.name,
            status=(
                OsintResultStatus.SUCCESS
                if is_well_formed
                else OsintResultStatus.FAILED
            ),
            confidence=(
                ConfidenceLevel.HIGH if is_well_formed else ConfidenceLevel.LOW
            ),
            duration_ms=int((time.perf_counter() - start) * 1000),
            data=output,
            sources=["syntactic-analysis"],
        )
