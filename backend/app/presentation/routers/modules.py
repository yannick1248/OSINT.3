from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.application.use_cases.run_module import RunModuleUseCase
from app.domain.modules.registry import ModuleNotFoundError, ModuleRegistry
from app.domain.scope import Scope
from app.presentation.dependencies import get_registry, get_run_module_use_case

router = APIRouter(prefix="/modules", tags=["modules"])


class RunModuleRequest(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)
    actor_id: str = Field(default="anonymous", max_length=255)
    scope: Scope = Field(default=Scope.SANDBOX_TEST)


@router.get("")
async def list_modules(
    registry: Annotated[ModuleRegistry, Depends(get_registry)],
) -> list[dict[str, Any]]:
    return [m.describe() for m in registry.all()]


@router.get("/{module_name}")
async def describe_module(
    module_name: str,
    registry: Annotated[ModuleRegistry, Depends(get_registry)],
) -> dict[str, Any]:
    try:
        return registry.get(module_name).describe()
    except ModuleNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "module not found") from exc


@router.post("/{module_name}/run")
async def run_module(
    module_name: str,
    payload: RunModuleRequest,
    use_case: Annotated[RunModuleUseCase, Depends(get_run_module_use_case)],
) -> dict[str, Any]:
    try:
        result = await use_case.execute(
            actor_id=payload.actor_id,
            module_name=module_name,
            raw_params=payload.params,
            scope=payload.scope,
        )
    except ModuleNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "module not found") from exc
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    return result.model_dump(mode="json")
