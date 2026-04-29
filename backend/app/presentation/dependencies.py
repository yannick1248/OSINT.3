from __future__ import annotations

from functools import lru_cache

from app.application.ports import AuditSink
from app.application.use_cases.run_module import RunModuleUseCase
from app.domain.modules.registry import ModuleRegistry
from app.infrastructure.audit.in_memory import InMemoryAuditSink
from app.infrastructure.modules import build_default_registry


@lru_cache(maxsize=1)
def get_registry() -> ModuleRegistry:
    return build_default_registry()


@lru_cache(maxsize=1)
def get_audit_sink() -> AuditSink:
    return InMemoryAuditSink()


def get_run_module_use_case() -> RunModuleUseCase:
    return RunModuleUseCase(registry=get_registry(), audit_sink=get_audit_sink())
