from app.domain.modules.registry import ModuleRegistry
from app.infrastructure.modules.domain_lookup import DomainLookupModule


def build_default_registry() -> ModuleRegistry:
    registry = ModuleRegistry()
    registry.register(DomainLookupModule())
    return registry


__all__ = ["DomainLookupModule", "build_default_registry"]
