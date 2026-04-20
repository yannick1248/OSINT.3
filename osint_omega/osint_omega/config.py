"""Chargement de la configuration `config.yaml`."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATHS = (
    Path("config.yaml"),
    Path("/etc/osint_omega/config.yaml"),
)


@dataclass(slots=True)
class TorConfig:
    enabled: bool = False
    proxy: str = "socks5://127.0.0.1:9050"
    control_port: int = 9051


@dataclass(slots=True)
class CacheConfig:
    enabled: bool = True
    ttl_seconds: int = 86_400
    db_path: str = "data/cache.db"


@dataclass(slots=True)
class LoggingConfig:
    level: str = "INFO"
    file: str = "data/logs/omega.log"


@dataclass(slots=True)
class Config:
    tor: TorConfig = field(default_factory=TorConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    apis: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path | None = None) -> Config:
        raw: dict[str, Any] = {}
        candidates = [Path(path)] if path else list(DEFAULT_CONFIG_PATHS)
        for candidate in candidates:
            if candidate.exists():
                raw = yaml.safe_load(candidate.read_text()) or {}
                break
        cfg = cls(
            tor=TorConfig(**(raw.get("tor") or {})),
            cache=CacheConfig(**(raw.get("cache") or {})),
            logging=LoggingConfig(**(raw.get("logging") or {})),
            apis=dict(raw.get("apis") or {}),
        )
        cfg._merge_env()
        return cfg

    def _merge_env(self) -> None:
        for key in ("shodan", "virustotal", "securitytrails", "hibp"):
            env_key = f"{key.upper()}_API_KEY"
            if env_val := os.environ.get(env_key):
                self.apis[key] = env_val
