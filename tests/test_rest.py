"""Unit tests — FastAPI REST interface, including the network globe page."""
from __future__ import annotations
import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # pylint: disable=wrong-import-position

from aetherlinkos.core.kernel import AetherKernel  # pylint: disable=wrong-import-position
from aetherlinkos.api.rest import build_app  # pylint: disable=wrong-import-position

# pylint: disable=redefined-outer-name  # standard pytest fixture injection


@pytest.fixture()
def client() -> TestClient:
    """A TestClient wired to a fresh kernel-backed app."""
    app = build_app(AetherKernel())
    assert app is not None
    return TestClient(app)


def test_status_endpoint(client: TestClient) -> None:
    """/status returns the kernel snapshot with verath and plugin sections."""
    resp = client.get("/status")
    assert resp.status_code == 200
    body = resp.json()
    assert "verath" in body
    assert "plugins" in body


def test_globe_page_serves_html(client: TestClient) -> None:
    """/globe serves the cobe globe page as HTML."""
    resp = client.get("/globe")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/html")
    assert "createGlobe" in resp.text
    assert '<canvas id="cobe"' in resp.text


def test_globe_page_has_bindable_markers(client: TestClient) -> None:
    """The globe page wires cobe's bindable marker/arc CSS variables."""
    text = client.get("/globe").text
    assert "--cobe-visible-sf" in text
    assert "--cobe-arc-sf-tokyo" in text
