"""Moteur d'orchestration : sélection d'outils, cache, exécution parallèle."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable
from typing import Sequence

from osint_omega.cache import ResultCache
from osint_omega.config import Config
from osint_omega.gate import GateDecision, LegalEthicsGate
from osint_omega.tools import DEFAULT_TOOLS, Tool
from osint_omega.types import (
    Confidence,
    Mission,
    Scope,
    Target,
    ToolResult,
    ToolStatus,
)

logger = logging.getLogger(__name__)


class Engine:
    """Orchestrateur central.

    Responsabilités :
    - filtrer la mission via ``LegalEthicsGate`` ;
    - choisir les outils qui supportent le type de cible ;
    - interroger le cache, exécuter les outils manquants en parallèle ;
    - assembler une ``Mission`` normalisée.
    """

    def __init__(
        self,
        *,
        config: Config | None = None,
        tools: Sequence[Tool] | None = None,
        cache: ResultCache | None = None,
        gate: LegalEthicsGate | None = None,
    ) -> None:
        self.config = config or Config.load()
        self.tools: list[Tool] = list(tools) if tools is not None else list(DEFAULT_TOOLS)
        self.gate = gate or LegalEthicsGate()
        if cache is not None:
            self.cache = cache
        elif self.config.cache.enabled:
            self.cache = ResultCache(
                self.config.cache.db_path,
                ttl_seconds=self.config.cache.ttl_seconds,
            )
        else:
            self.cache = None

    def select_tools(
        self, target: Target, only: Iterable[str] | None = None
    ) -> list[Tool]:
        chosen = [t for t in self.tools if t.supports(target.type)]
        if only:
            wanted = set(only)
            chosen = [t for t in chosen if t.name in wanted]
        return chosen

    async def run(
        self,
        target: Target,
        scope: Scope,
        *,
        only: Iterable[str] | None = None,
        actor_id: str = "anonymous",
    ) -> Mission:
        decision = self.gate.evaluate(target, scope)
        if not decision.allowed:
            return Mission(
                target=target,
                scope=scope,
                actor_id=actor_id,
                results=[
                    ToolResult(
                        source="legal_ethics_gate",
                        status=ToolStatus.OUT_OF_SCOPE,
                        confidence=Confidence.LOW,
                        error="; ".join(decision.notes) or "Out of scope.",
                    )
                ],
                gate_notes=list(decision.notes),
            )

        selected = self.select_tools(target, only=only)
        if not selected:
            return Mission(
                target=target,
                scope=scope,
                actor_id=actor_id,
                results=[
                    ToolResult(
                        source="engine",
                        status=ToolStatus.SKIPPED,
                        confidence=Confidence.LOW,
                        error=f"Aucun outil pour le type {target.type.value}.",
                    )
                ],
                gate_notes=list(decision.notes),
            )

        results = await self._execute(selected, target)
        return Mission(
            target=target,
            scope=scope,
            actor_id=actor_id,
            results=results,
            gate_notes=list(decision.notes),
        )

    async def _execute(self, tools: Sequence[Tool], target: Target) -> list[ToolResult]:
        async def run_one(tool: Tool) -> ToolResult:
            if self.cache is not None:
                cached = self.cache.get(tool.cache_key(target))
                if cached is not None:
                    logger.info("cache_hit source=%s target=%s", tool.name, target.value)
                    return cached
            try:
                result = await tool.run(target)
            except Exception as exc:  # noqa: BLE001 — we want tool isolation
                logger.exception("tool_failure source=%s", tool.name)
                result = ToolResult(
                    source=tool.name,
                    status=ToolStatus.FAILED,
                    confidence=Confidence.LOW,
                    error=f"{type(exc).__name__}: {exc}",
                )
            if self.cache is not None and result.status == ToolStatus.SUCCESS:
                self.cache.set(tool.cache_key(target), result)
            return result

        return list(await asyncio.gather(*(run_one(t) for t in tools)))

    def describe_tools(self) -> list[dict]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "supported_targets": sorted(x.value for x in t.supported_targets),
            }
            for t in self.tools
        ]

    def close(self) -> None:
        if self.cache is not None:
            self.cache.close()


def detect_target_type(value: str) -> Target:
    """Déduit automatiquement le type d'une cible (heuristique simple)."""
    from osint_omega.types import TargetType

    v = value.strip()
    if "@" in v and "." in v.split("@")[-1]:
        t = TargetType.EMAIL
    elif v.endswith(".onion"):
        t = TargetType.ONION
    elif v.replace(".", "").isdigit() and v.count(".") == 3:
        t = TargetType.IP
    elif "." in v and " " not in v:
        t = TargetType.DOMAIN
    elif " " in v:
        t = TargetType.FREE_TEXT
    else:
        t = TargetType.USERNAME
    return Target(value=v, type=t)
