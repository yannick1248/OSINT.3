"""Module FastAPI qui expose l'orchestrateur osint_omega via l'API.

Import paresseux : si le paquet ``osint_omega`` n'est pas installé, le module
retourne un résultat ``FAILED`` plutôt que de faire crasher le backend.
"""

from __future__ import annotations

import time
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from app.domain.modules.base import (
    ConfidenceLevel,
    OsintModule,
    OsintResult,
    OsintResultStatus,
)


class OmegaOrchestratorParams(BaseModel):
    target: str = Field(..., min_length=1, max_length=512)
    target_type: str | None = Field(
        default=None,
        description="email | domain | username | ip | onion | person | company | free_text",
    )
    scope: str = Field(
        default="SANDBOX_TEST",
        description="Périmètre osint_omega (SANDBOX_TEST, OWNED_ASSETS, ...).",
    )
    only: list[str] | None = Field(
        default=None,
        description="Restreindre à une sous-liste d'outils (par `name`).",
    )


class OmegaOrchestratorOutput(BaseModel):
    mission: dict[str, Any]


class OmegaOrchestratorModule(OsintModule[OmegaOrchestratorParams, OmegaOrchestratorOutput]):
    name: ClassVar[str] = "omega_orchestrator"
    description: ClassVar[str] = (
        "Orchestrateur multi-outils osint_omega (cache SQLite, exécution parallèle, "
        "gate légal)."
    )
    input_schema: ClassVar[type[BaseModel]] = OmegaOrchestratorParams
    output_schema: ClassVar[type[BaseModel]] = OmegaOrchestratorOutput

    async def validate_input(self, params: OmegaOrchestratorParams) -> bool:
        return bool(params.target.strip())

    async def execute(
        self, params: OmegaOrchestratorParams
    ) -> OsintResult[OmegaOrchestratorOutput]:
        started = time.perf_counter()
        try:
            from osint_omega import Engine, Scope, Target, TargetType  # noqa: PLC0415
            from osint_omega.engine import detect_target_type  # noqa: PLC0415
        except ImportError as exc:
            return OsintResult[OmegaOrchestratorOutput](
                module=self.name,
                status=OsintResultStatus.FAILED,
                confidence=ConfidenceLevel.LOW,
                duration_ms=int((time.perf_counter() - started) * 1000),
                errors=[f"osint_omega not installed: {exc}"],
            )

        target = (
            Target(value=params.target, type=TargetType(params.target_type))
            if params.target_type
            else detect_target_type(params.target)
        )
        engine = Engine()
        try:
            mission = await engine.run(
                target,
                scope=Scope(params.scope),
                only=params.only,
                actor_id="api",
            )
        finally:
            engine.close()

        confidence = ConfidenceLevel(mission.aggregated_confidence.value)
        has_success = any(r.status.value == "SUCCESS" for r in mission.results)
        status = (
            OsintResultStatus.SUCCESS if has_success else OsintResultStatus.PARTIAL
        )
        return OsintResult[OmegaOrchestratorOutput](
            module=self.name,
            status=status,
            confidence=confidence,
            duration_ms=int((time.perf_counter() - started) * 1000),
            data=OmegaOrchestratorOutput(mission=mission.model_dump(mode="json")),
            sources=[r.source for r in mission.results],
        )
