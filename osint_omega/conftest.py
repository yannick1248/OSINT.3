"""Minimal async test runner compatible with plain pytest (no plugin required)."""

from __future__ import annotations

import asyncio
import inspect


def pytest_pyfunc_call(pyfuncitem):
    """Run ``async def`` tests via ``asyncio.run`` when pytest-asyncio is absent."""
    test_func = pyfuncitem.obj
    if not inspect.iscoroutinefunction(test_func):
        return None

    kwargs = {
        arg: pyfuncitem.funcargs[arg]
        for arg in pyfuncitem._fixtureinfo.argnames
        if arg in pyfuncitem.funcargs
    }
    asyncio.run(test_func(**kwargs))
    return True
