from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.presentation.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_root_shows_disclaimer(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert "disclaimer" in body
    assert "légal" in body["disclaimer"].lower()


def test_list_modules_includes_sample(client: TestClient) -> None:
    r = client.get("/modules")
    assert r.status_code == 200
    names = [m["name"] for m in r.json()]
    assert "domain_lookup" in names


def test_run_domain_lookup(client: TestClient) -> None:
    r = client.post(
        "/modules/domain_lookup/run",
        json={"actor_id": "tester", "params": {"domain": "example.com"}},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "SUCCESS"
    assert body["data"]["tld"] == "com"


def test_run_unknown_module_returns_404(client: TestClient) -> None:
    r = client.post("/modules/nope/run", json={"params": {}})
    assert r.status_code == 404
