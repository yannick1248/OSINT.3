"""Périmètres de mission (alignés sur le prompt multi-agent forensique)."""

from __future__ import annotations

from enum import StrEnum


class Scope(StrEnum):
    SANDBOX_TEST = "SANDBOX_TEST"
    OWNED_ASSETS = "OWNED_ASSETS"
    CLIENT_AUTHORIZED_SCOPE = "CLIENT_AUTHORIZED_SCOPE"
    PUBLIC_INTEREST_RESEARCH = "PUBLIC_INTEREST_RESEARCH"
    INTERNAL_AUDIT = "INTERNAL_AUDIT"
    LEGALLY_RESTRICTED = "LEGALLY_RESTRICTED"
