#!/usr/bin/env python3
"""Entrée CLI canonique — équivalent à `python -m osint_omega`.

Utilisation :
    python omega.py --target example.com --type domain --scope OWNED_ASSETS
    python omega.py --target alice@example.com --scope SANDBOX_TEST --pretty
    python omega.py --list-tools
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permet l'exécution sans installation (`python omega.py ...`).
_LOCAL_PKG = Path(__file__).resolve().parent / "osint_omega"
if (_LOCAL_PKG / "osint_omega" / "__init__.py").exists():
    sys.path.insert(0, str(_LOCAL_PKG))

from osint_omega.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
