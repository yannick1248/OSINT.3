"""Cache SQLite persistant pour les résultats d'outils."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from osint_omega.types import ToolResult

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tool_cache (
    key TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    stored_at INTEGER NOT NULL,
    expires_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tool_cache_expires ON tool_cache(expires_at);
"""


class ResultCache:
    """Cache simple clé/valeur avec TTL.

    La clé est construite par le moteur sous la forme `tool:target_type:target`.
    `:memory:` est accepté pour les tests unitaires.
    """

    def __init__(self, db_path: str | Path, ttl_seconds: int) -> None:
        self.ttl_seconds = int(ttl_seconds)
        self._is_memory = str(db_path) == ":memory:"
        if not self._is_memory:
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(
            str(db_path), detect_types=sqlite3.PARSE_DECLTYPES
        )
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def get(self, key: str) -> ToolResult | None:
        now = int(time.time())
        cur = self._conn.execute(
            "SELECT payload, expires_at FROM tool_cache WHERE key = ?",
            (key,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        payload, expires_at = row
        if expires_at <= now:
            self._conn.execute("DELETE FROM tool_cache WHERE key = ?", (key,))
            self._conn.commit()
            return None
        data = json.loads(payload)
        data["cache_hit"] = True
        return ToolResult.model_validate(data)

    def set(self, key: str, result: ToolResult) -> None:
        now = int(time.time())
        expires_at = now + self.ttl_seconds
        payload = result.model_dump_json()
        self._conn.execute(
            "INSERT OR REPLACE INTO tool_cache(key, payload, stored_at, expires_at) "
            "VALUES (?, ?, ?, ?)",
            (key, payload, now, expires_at),
        )
        self._conn.commit()

    def purge_expired(self) -> int:
        now = int(time.time())
        cur = self._conn.execute(
            "DELETE FROM tool_cache WHERE expires_at <= ?", (now,)
        )
        self._conn.commit()
        return cur.rowcount

    def close(self) -> None:
        self._conn.close()
