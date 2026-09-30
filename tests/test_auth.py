"""Unit tests — API key authentication for the REST server."""
from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from aetherlinkos.api.auth import (
    API_KEY_ENV_VAR,
    API_KEY_HEADER,
    api_key_dependency,
    load_keys_from_env,
    protect_app,
)


def _app_with_route() -> FastAPI:
    app = FastAPI()

    @app.get("/ping")
    async def ping() -> dict:
        return {"ok": True}

    return app


def test_no_keys_configured_means_open_access(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(API_KEY_ENV_VAR, raising=False)
    app = protect_app(_app_with_route())
    client = TestClient(app)
    assert client.get("/ping").status_code == 200


def test_valid_key_is_accepted() -> None:
    app = protect_app(_app_with_route(), keys=["secret-a", "secret-b"])
    client = TestClient(app)
    r = client.get("/ping", headers={API_KEY_HEADER: "secret-b"})
    assert r.status_code == 200


def test_missing_key_returns_401() -> None:
    app = protect_app(_app_with_route(), keys=["secret"])
    client = TestClient(app)
    r = client.get("/ping")
    assert r.status_code == 401


def test_wrong_key_returns_403() -> None:
    app = protect_app(_app_with_route(), keys=["secret"])
    client = TestClient(app)
    r = client.get("/ping", headers={API_KEY_HEADER: "nope"})
    assert r.status_code == 403


def test_load_keys_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(API_KEY_ENV_VAR, "  one , two,, three ")
    assert load_keys_from_env() == ("one", "two", "three")


def test_dependency_returns_matched_key_directly() -> None:
    app = FastAPI()
    dep = api_key_dependency(["alpha"])

    @app.get("/whoami")
    async def whoami(key: str | None = Depends(dep)) -> dict:
        return {"key": key}

    client = TestClient(app)
    r = client.get("/whoami", headers={API_KEY_HEADER: "alpha"})
    assert r.status_code == 200
    assert r.json() == {"key": "alpha"}
