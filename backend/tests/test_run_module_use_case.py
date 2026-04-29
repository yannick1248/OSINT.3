from __future__ import annotations

import pytest

from app.application.use_cases.run_module import RunModuleUseCase
from app.domain.modules.registry import ModuleNotFoundError
from app.infrastructure.audit.in_memory import InMemoryAuditSink
from app.infrastructure.modules import build_default_registry


@pytest.fixture
def use_case() -> tuple[RunModuleUseCase, InMemoryAuditSink]:
    audit = InMemoryAuditSink()
    return (
        RunModuleUseCase(registry=build_default_registry(), audit_sink=audit),
        audit,
    )


async def test_runs_registered_module_and_records_audit(
    use_case: tuple[RunModuleUseCase, InMemoryAuditSink],
) -> None:
    uc, audit = use_case
    result = await uc.execute(
        actor_id="analyst-1",
        module_name="domain_lookup",
        raw_params={"domain": "example.com"},
    )
    assert result.status.value == "SUCCESS"
    assert len(audit.events) == 1
    assert audit.events[0].actor_id == "analyst-1"
    assert audit.events[0].module == "domain_lookup"


async def test_unknown_module_raises(
    use_case: tuple[RunModuleUseCase, InMemoryAuditSink],
) -> None:
    uc, _ = use_case
    with pytest.raises(ModuleNotFoundError):
        await uc.execute(
            actor_id="analyst-1",
            module_name="does_not_exist",
            raw_params={},
        )
