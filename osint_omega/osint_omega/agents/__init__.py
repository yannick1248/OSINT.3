"""Prompts et artefacts d'orchestration multi-agent."""

from __future__ import annotations

from pathlib import Path

AGENTS_DIR = Path(__file__).parent

SYSTEM_PROMPT_PATH = AGENTS_DIR / "system_prompt.xml"


def load_system_prompt() -> str:
    """Retourne le prompt système multi-agent forensique (XML)."""
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


__all__ = ["AGENTS_DIR", "SYSTEM_PROMPT_PATH", "load_system_prompt"]
