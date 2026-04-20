from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.application.ports import AuditSink
from app.domain.audit import AuditEvent
from app.domain.modules.base import OsintResult
from app.domain.modules.registry import ModuleRegistry


@dataclass(slots=True)
class RunModuleUseCase:
    registry: ModuleRegistry
    audit_sink: AuditSink

    async def execute(
        self,
        *,
        actor_id: str,
        module_name: str,
        raw_params: dict[str, Any],
    ) -> OsintResult[Any]:
        module = self.registry.get(module_name)
        params = module.input_schema.model_validate(raw_params)
        if not await module.validate_input(params):  # type: ignore[arg-type]
            raise ValueError(f"Invalid input for module '{module_name}'")

        result = await module.execute(params)  # type: ignore[arg-type]

        await self.audit_sink.record(
            AuditEvent(
                actor_id=actor_id,
                module=module_name,
                params=raw_params,
                result_id=result.result_id,
                outcome=result.status.value,
            )
        )
        return result
