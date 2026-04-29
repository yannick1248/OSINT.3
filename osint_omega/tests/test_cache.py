from __future__ import annotations

import time

from osint_omega.cache import ResultCache
from osint_omega.types import Confidence, ToolResult, ToolStatus


def _make_result() -> ToolResult:
    return ToolResult(
        source="fake",
        status=ToolStatus.SUCCESS,
        confidence=Confidence.HIGH,
        data={"k": "v"},
    )


def test_cache_roundtrip_sets_cache_hit_flag() -> None:
    cache = ResultCache(":memory:", ttl_seconds=60)
    cache.set("key", _make_result())
    hit = cache.get("key")
    assert hit is not None
    assert hit.cache_hit is True
    assert hit.data == {"k": "v"}


def test_cache_miss_returns_none() -> None:
    cache = ResultCache(":memory:", ttl_seconds=60)
    assert cache.get("absent") is None


def test_cache_expires_after_ttl() -> None:
    cache = ResultCache(":memory:", ttl_seconds=0)
    cache.set("k", _make_result())
    time.sleep(0.01)
    assert cache.get("k") is None
