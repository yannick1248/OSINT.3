from __future__ import annotations

import asyncio
from typing import ClassVar

from osint_omega.cache import ResultCache
from osint_omega.config import CacheConfig, Config
from osint_omega.engine import Engine, detect_target_type
from osint_omega.tools.base import Tool
from osint_omega.types import (
    Confidence,
    Mission,
    Scope,
    Target,
    TargetType,
    ToolResult,
    ToolStatus,
)


class FakeTool(Tool):
    name: ClassVar[str] = "fake_domain"
    description: ClassVar[str] = "Fake domain tool for tests."
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.DOMAIN})

    def __init__(self) -> None:
        self.calls = 0

    async def run(self, target: Target) -> ToolResult:
        self.calls += 1
        await asyncio.sleep(0)
        return ToolResult(
            source=self.name,
            status=ToolStatus.SUCCESS,
            confidence=Confidence.HIGH,
            data={"target": target.value},
        )


class EmailOnlyTool(Tool):
    name: ClassVar[str] = "email_only"
    description: ClassVar[str] = "Only supports emails."
    supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.EMAIL})

    async def run(self, target: Target) -> ToolResult:
        return ToolResult(
            source=self.name, status=ToolStatus.SUCCESS, confidence=Confidence.MEDIUM
        )


def _engine_with(tools: list[Tool]) -> Engine:
    cfg = Config(cache=CacheConfig(enabled=False))
    return Engine(config=cfg, tools=tools, cache=None)


async def test_engine_runs_only_matching_tools() -> None:
    domain_tool, email_tool = FakeTool(), EmailOnlyTool()
    engine = _engine_with([domain_tool, email_tool])
    mission = await engine.run(
        Target(value="example.com", type=TargetType.DOMAIN),
        scope=Scope.OWNED_ASSETS,
    )
    assert isinstance(mission, Mission)
    sources = [r.source for r in mission.results]
    assert "fake_domain" in sources
    assert "email_only" not in sources


async def test_engine_aggregated_confidence_bonus_with_corroboration() -> None:
    class H(Tool):
        name: ClassVar[str] = "h1"
        description: ClassVar[str] = ""
        supported_targets: ClassVar[frozenset[TargetType]] = frozenset({TargetType.DOMAIN})

        async def run(self, target: Target) -> ToolResult:
            return ToolResult(
                source=self.name,
                status=ToolStatus.SUCCESS,
                confidence=Confidence.HIGH,
            )

    tools = []
    for i in range(3):
        cls = type(f"H{i}", (H,), {"name": f"h{i}"})
        tools.append(cls())
    engine = _engine_with(tools)
    mission = await engine.run(
        Target(value="example.com", type=TargetType.DOMAIN),
        scope=Scope.OWNED_ASSETS,
    )
    assert mission.aggregated_confidence is Confidence.VERY_HIGH


async def test_engine_blocks_legally_restricted() -> None:
    engine = _engine_with([FakeTool()])
    mission = await engine.run(
        Target(value="example.com", type=TargetType.DOMAIN),
        scope=Scope.LEGALLY_RESTRICTED,
    )
    assert all(r.status is ToolStatus.OUT_OF_SCOPE for r in mission.results)


async def test_engine_uses_cache_on_second_call() -> None:
    fake = FakeTool()
    cache = ResultCache(":memory:", ttl_seconds=60)
    engine = Engine(config=Config(), tools=[fake], cache=cache)
    target = Target(value="example.com", type=TargetType.DOMAIN)
    await engine.run(target, scope=Scope.OWNED_ASSETS)
    await engine.run(target, scope=Scope.OWNED_ASSETS)
    assert fake.calls == 1


async def test_engine_respects_only_filter() -> None:
    a, b = FakeTool(), FakeTool()
    b.name = "fake_b"  # type: ignore[misc]
    engine = _engine_with([a, b])
    mission = await engine.run(
        Target(value="example.com", type=TargetType.DOMAIN),
        scope=Scope.OWNED_ASSETS,
        only=["fake_domain"],
    )
    sources = {r.source for r in mission.results}
    assert sources == {"fake_domain"}


def test_detect_target_type_routing() -> None:
    assert detect_target_type("alice@example.com").type is TargetType.EMAIL
    assert detect_target_type("example.com").type is TargetType.DOMAIN
    assert detect_target_type("abcdef1234.onion").type is TargetType.ONION
    assert detect_target_type("192.168.1.1").type is TargetType.IP
    assert detect_target_type("john_doe").type is TargetType.USERNAME
    assert detect_target_type("john doe").type is TargetType.FREE_TEXT
