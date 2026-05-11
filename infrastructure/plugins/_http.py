"""Small async HTTP helpers built on the standard library.

The backend intentionally avoids forcing a heavy client dependency into plugin imports;
network calls are isolated here and run in a thread so plugin APIs remain async.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_HEADERS = {"User-Agent": "OSINT.3/1.0 (+missing-person-investigation)"}


class HttpError(RuntimeError):
    pass


def _request(method: str, url: str, *, headers: dict[str, str] | None = None, timeout: float = 20.0, data: bytes | None = None) -> tuple[int, bytes, dict[str, str]]:
    request = Request(url, data=data, method=method, headers={**DEFAULT_HEADERS, **(headers or {})})
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - URLs are fixed/provider URLs or explicit operator config.
            return response.status, response.read(), dict(response.headers.items())
    except HTTPError as exc:
        body = exc.read()
        raise HttpError(f"HTTP {exc.code} for {url}: {body[:300]!r}") from exc
    except URLError as exc:
        raise HttpError(f"network error for {url}: {exc.reason}") from exc


async def get_json(url: str, *, headers: dict[str, str] | None = None, timeout: float = 20.0) -> Any:
    status, body, _ = await asyncio.to_thread(_request, "GET", url, headers=headers, timeout=timeout)
    if status >= 400:
        raise HttpError(f"HTTP {status} for {url}")
    return json.loads(body.decode("utf-8", errors="replace"))


async def get_text(url: str, *, headers: dict[str, str] | None = None, timeout: float = 20.0) -> str:
    status, body, _ = await asyncio.to_thread(_request, "GET", url, headers=headers, timeout=timeout)
    if status >= 400:
        raise HttpError(f"HTTP {status} for {url}")
    return body.decode("utf-8", errors="replace")


def with_query(base_url: str, params: dict[str, str | int]) -> str:
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}{urlencode(params)}"
