from __future__ import annotations

import importlib
from pathlib import Path


def test_app_main_imports_without_optional_runtime_dependencies() -> None:
    module = importlib.import_module("app.main")
    assert hasattr(module, "app")


def test_web_console_assets_exist_and_are_wired() -> None:
    root = Path("app/static")
    html = (root / "index.html").read_text(encoding="utf-8")
    script = (root / "app.js").read_text(encoding="utf-8")
    styles = (root / "styles.css").read_text(encoding="utf-8")

    assert "Console Web réactive" in html
    assert "/api/v1/modules" in script
    assert "/api/v1/investigate/missing-person" in script
    assert "@media (max-width: 860px)" in styles
