"""Plugin registry — discovery, loading, and lifecycle tracking."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aetherlinkos.plugin.base import BasePlugin

_REQUIRED_MANIFEST_FIELDS = {"id", "name", "version", "entry"}


class PluginRegistry:
    """Discovers, loads, and tracks AetherLinkOS plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, "BasePlugin"] = {}
        self._manifests: dict[str, dict] = {}

    def discover(self, plugin_dir: Path) -> list[Path]:
        """Return subdirectories of plugin_dir that contain manifest.json."""
        if not plugin_dir.is_dir():
            return []
        return [p for p in plugin_dir.iterdir()
                if p.is_dir() and (p / "manifest.json").exists()]

    def load_manifest(self, plugin_path: Path) -> dict:
        manifest = json.loads((plugin_path / "manifest.json").read_text())
        missing = _REQUIRED_MANIFEST_FIELDS - manifest.keys()
        if missing:
            raise ValueError(f"Plugin at {plugin_path} manifest missing: {missing}")
        return manifest

    def load_plugin_class(self, plugin_path: Path, manifest: dict) -> type:
        entry = manifest["entry"]
        module_file = plugin_path / f"{entry}.py"
        spec = importlib.util.spec_from_file_location(entry, module_file)
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        class_name = manifest.get("class", "Plugin")
        return getattr(module, class_name)

    def register(self, plugin: "BasePlugin", manifest: dict) -> None:
        pid = manifest["id"]
        self._plugins[pid] = plugin
        self._manifests[pid] = manifest

    def unregister(self, plugin_id: str) -> None:
        self._plugins.pop(plugin_id, None)
        self._manifests.pop(plugin_id, None)

    def get(self, plugin_id: str) -> "BasePlugin | None":
        return self._plugins.get(plugin_id)

    def all_ids(self) -> list[str]:
        return list(self._plugins.keys())

    def manifest(self, plugin_id: str) -> dict | None:
        return self._manifests.get(plugin_id)
