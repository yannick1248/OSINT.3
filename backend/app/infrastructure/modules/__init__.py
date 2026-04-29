from app.domain.modules.registry import ModuleRegistry
from app.infrastructure.modules.domain_lookup import DomainLookupModule
from app.infrastructure.modules.omega_orchestrator import OmegaOrchestratorModule


def build_default_registry() -> ModuleRegistry:
    registry = ModuleRegistry()
    registry.register(DomainLookupModule())
    registry.register(OmegaOrchestratorModule())
    return registry


__all__ = [
    "DomainLookupModule",
    "OmegaOrchestratorModule",
    "build_default_registry",
]
