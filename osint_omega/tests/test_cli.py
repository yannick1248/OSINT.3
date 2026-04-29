from __future__ import annotations

import json
import sys
from io import StringIO

from osint_omega.cli import main


def test_cli_list_tools(monkeypatch) -> None:
    monkeypatch.setattr(sys, "stdout", StringIO())
    rc = main(["--list-tools"])
    assert rc == 0
    payload = json.loads(sys.stdout.getvalue())
    names = {t["name"] for t in payload["tools"]}
    assert "domain_syntax" in names
    assert "crtsh" in names


def test_cli_runs_domain_syntax_with_scope(monkeypatch) -> None:
    monkeypatch.setattr(sys, "stdout", StringIO())
    rc = main(
        [
            "--target",
            "example.com",
            "--type",
            "domain",
            "--scope",
            "OWNED_ASSETS",
            "--only",
            "domain_syntax",
            "--pretty",
        ]
    )
    assert rc == 0
    payload = json.loads(sys.stdout.getvalue())
    assert payload["scope"] == "OWNED_ASSETS"
    sources = [r["source"] for r in payload["results"]]
    assert sources == ["domain_syntax"]


def test_cli_legally_restricted_returns_out_of_scope(monkeypatch) -> None:
    monkeypatch.setattr(sys, "stdout", StringIO())
    main(
        [
            "--target",
            "example.com",
            "--type",
            "domain",
            "--scope",
            "LEGALLY_RESTRICTED",
        ]
    )
    payload = json.loads(sys.stdout.getvalue())
    assert all(r["status"] == "OUT_OF_SCOPE" for r in payload["results"])
