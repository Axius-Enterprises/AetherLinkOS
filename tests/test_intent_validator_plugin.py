"""Unit tests — Intent Content Consistency Validator Plugin."""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

# Mock the plugin before import
pytest_plugins = []


@pytest.fixture
def mock_kernel():
    """Create a mock kernel for testing."""
    kernel = AsyncMock()
    kernel.events = AsyncMock()
    kernel.events.subscribe = MagicMock()
    kernel.events.unsubscribe = MagicMock()
    kernel.events.publish = AsyncMock()
    return kernel


@pytest.fixture
def validator_plugin(mock_kernel):
    """Create validator plugin instance for testing."""
    from aetherlinkos.plugin.base import BasePlugin
    from plugins.intent_content_validator.plugin import Plugin

    plugin = Plugin(kernel=mock_kernel)
    plugin.manifest = {"id": "intent-content-validator", "name": "Intent Content Validator", "version": "0.1.0"}
    return plugin


def test_plugin_initializes(validator_plugin):
    """Test plugin initialization."""
    validator_plugin.on_initialize()
    assert validator_plugin._service_process is None
    assert validator_plugin._http_client is None
    assert validator_plugin._service_ready is False


@pytest.mark.asyncio
async def test_plugin_activates_subscribes(validator_plugin, mock_kernel):
    """Test plugin activation subscribes to events."""
    validator_plugin.on_activate()
    # Give the create_task a moment to execute
    await asyncio.sleep(0.01)
    # Verify subscription was called
    assert mock_kernel.events.subscribe.called


@pytest.mark.asyncio
async def test_plugin_deactivates_unsubscribes(validator_plugin, mock_kernel):
    """Test plugin deactivation unsubscribes from events."""
    validator_plugin.on_activate()
    await asyncio.sleep(0.01)
    validator_plugin.on_deactivate()
    await asyncio.sleep(0.01)
    # Verify unsubscription was called
    assert mock_kernel.events.unsubscribe.called


@pytest.mark.asyncio
async def test_validate_with_service_ready(validator_plugin):
    """Test validate method when service is ready."""
    # Mock ready state
    validator_plugin._service_ready = True
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {"valid": True, "issues": []},
    }
    mock_client.post = AsyncMock(return_value=mock_response)
    validator_plugin._http_client = mock_client

    # Test validation
    result = await validator_plugin.validate("Test content")
    assert result["success"] is True
    assert mock_client.post.called


@pytest.mark.asyncio
async def test_validate_raises_when_not_ready(validator_plugin):
    """Test validate raises error when service is not ready."""
    validator_plugin._service_ready = False
    validator_plugin._http_client = None

    with pytest.raises(RuntimeError, match="not ready"):
        await validator_plugin.validate("Test content")


@pytest.mark.asyncio
async def test_validate_batch_with_service_ready(validator_plugin):
    """Test validate_batch method when service is ready."""
    validator_plugin._service_ready = True
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": [
            {"valid": True, "issues": []},
            {"valid": False, "issues": ["Issue 1"]},
        ],
    }
    mock_client.post = AsyncMock(return_value=mock_response)
    validator_plugin._http_client = mock_client

    # Test batch validation
    result = await validator_plugin.validate_batch(["Content 1", "Content 2"])
    assert result["success"] is True
    assert len(result["data"]) == 2
    assert mock_client.post.called


@pytest.mark.asyncio
async def test_validate_batch_raises_when_not_ready(validator_plugin):
    """Test validate_batch raises error when service is not ready."""
    validator_plugin._service_ready = False
    validator_plugin._http_client = None

    with pytest.raises(RuntimeError, match="not ready"):
        await validator_plugin.validate_batch(["Content 1"])


@pytest.mark.asyncio
async def test_validate_handles_http_error(validator_plugin):
    """Test validate handles HTTP errors correctly."""
    validator_plugin._service_ready = True
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    mock_client.post = AsyncMock(return_value=mock_response)
    validator_plugin._http_client = mock_client

    with pytest.raises(RuntimeError, match="Validation failed"):
        await validator_plugin.validate("Test content")


def test_plugin_has_service_constants(validator_plugin):
    """Test plugin has expected service configuration."""
    assert validator_plugin.SERVICE_PORT == 3001
    assert validator_plugin.SERVICE_HOST == "127.0.0.1"
    assert validator_plugin.SERVICE_URL == "http://127.0.0.1:3001"
    assert validator_plugin.SERVICE_TIMEOUT == 10.0


def test_manifest_file_exists():
    """Test manifest.json exists for plugin."""
    manifest_path = Path(__file__).parent.parent / "plugins" / "intent_content_validator" / "manifest.json"
    assert manifest_path.exists()
    # Could add JSON parsing validation here


def test_node_service_package_exists():
    """Test Node.js service package.json exists."""
    package_path = Path(__file__).parent.parent / "plugins" / "intent_content_validator_js" / "package.json"
    assert package_path.exists()
