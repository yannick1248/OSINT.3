from __future__ import annotations

from app.domain.modules.base import OsintModule


class ModuleNotFoundError(KeyError):
    pass


class ModuleRegistry:
    """Registre en mémoire des modules OSINT disponibles."""

    def __init__(self) -> None:
        self._modules: dict[str, OsintModule] = {}

    def register(self, module: OsintModule) -> None:
        if module.name in self._modules:
            raise ValueError(f"Module already registered: {module.name}")
        self._modules[module.name] = module

    def get(self, name: str) -> OsintModule:
        try:
            return self._modules[name]
        except KeyError as exc:
            raise ModuleNotFoundError(name) from exc

    def all(self) -> list[OsintModule]:
        return list(self._modules.values())

    def __contains__(self, name: object) -> bool:
        return name in self._modules

    def __len__(self) -> int:
        return len(self._modules)
