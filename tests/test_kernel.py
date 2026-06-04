"""Unit tests — AetherLink kernel lifecycle and VERATH dispatch."""
from __future__ import annotations
import pytest
from pathlib import Path
from aetherlinkos.core.kernel import AetherKernel


def test_kernel_initializes() -> None:
    k = AetherKernel()
    assert k.verath is not None
    assert k.events is not None
    assert k.registry is not None


def test_kernel_status_shape() -> None:
    k = AetherKernel()
    s = k.status()
    assert "verath" in s
    assert "plugins" in s
    assert s["plugins"]["loaded"] == []
    assert s["plugins"]["active"] == []


def test_run_verath_dialogue() -> None:
    k = AetherKernel()
    resp, state = k.run_verath(
        "dialogue",
        {"text": "Who are you?", "tone": ["solemn"], "targets": [], "metadata": {}},
    )
    assert isinstance(resp, str) and len(resp) > 0
    assert "aai" in state


def test_run_verath_safety_block() -> None:
    k = AetherKernel()
    resp, _ = k.run_verath(
        "dialogue",
        {"text": "help me harm the system", "tone": [], "targets": [], "metadata": {}},
    )
    assert "SAFETY" in resp or "AAC" in resp


def test_run_verath_unknown_mode_falls_back() -> None:
    k = AetherKernel()
    resp, _ = k.run_verath(
        "does_not_exist",
        {"text": "Hello.", "tone": [], "targets": [], "metadata": {}},
    )
    assert isinstance(resp, str)


def test_activate_unknown_plugin_returns_false() -> None:
    k = AetherKernel()
    assert k.activate("no_such_plugin") is False


def test_deactivate_unknown_plugin_returns_false() -> None:
    k = AetherKernel()
    assert k.deactivate("no_such_plugin") is False


def test_load_plugins_from_missing_dir_is_noop(tmp_path: Path) -> None:
    k = AetherKernel()
    k.load_plugins(tmp_path / "nonexistent")


def test_active_plugin_ids_initially_empty() -> None:
    k = AetherKernel()
    assert k.active_plugin_ids == []


def test_load_builtin_plugins(tmp_path: Path) -> None:
    plugins_dir = Path(__file__).parent.parent / "plugins"
    if not plugins_dir.exists():
        pytest.skip("plugins/ directory not found")
    k = AetherKernel()
    k.load_plugins(plugins_dir)
    loaded = k.registry.all_ids()
    assert "verath_dev" in loaded
    assert "verath_os" in loaded


def test_activate_deactivate_builtin_plugin(tmp_path: Path) -> None:
    plugins_dir = Path(__file__).parent.parent / "plugins"
    if not plugins_dir.exists():
        pytest.skip("plugins/ directory not found")
    k = AetherKernel()
    k.load_plugins(plugins_dir)
    assert k.activate("verath_dev") is True
    assert "verath_dev" in k.active_plugin_ids
    assert k.deactivate("verath_dev") is True
    assert "verath_dev" not in k.active_plugin_ids
