"""AetherLink Kernel — central orchestrator of VERATH runtime, plugins, and events."""
from __future__ import annotations
import asyncio
from pathlib import Path
from typing import Any

from verath.verath_unified import VerathAPI
from aetherlinkos.core.events import EventBus, Event, EventType
from aetherlinkos.core.registry import PluginRegistry


class AetherKernel:
    """
    Central AetherLinkOS kernel.

    Responsibilities:
    - Owns the single shared VerathAPI instance.
    - Manages plugin lifecycle (discover → load → activate → deactivate).
    - Hosts the async event bus.
    - Exposes run_verath() as a unified dispatch point for all SDK tools.
    """

    def __init__(self, plugin_dirs: list[Path] | None = None) -> None:
        self.verath = VerathAPI()
        self.events = EventBus()
        self.registry = PluginRegistry()
        self._plugin_dirs: list[Path] = plugin_dirs or []
        self._active: set[str] = set()

    # ── Plugin management ─────────────────────────────────────────────────

    def load_plugins(self, plugin_dir: Path | None = None) -> None:
        """Discover and load all plugins from plugin_dir or configured dirs."""
        dirs = [plugin_dir] if plugin_dir else self._plugin_dirs
        for d in dirs:
            for path in self.registry.discover(d):
                self._load_one(path)

    def _load_one(self, plugin_path: Path) -> None:
        try:
            manifest = self.registry.load_manifest(plugin_path)
            cls = self.registry.load_plugin_class(plugin_path, manifest)
            instance = cls(kernel=self)
            self.registry.register(instance, manifest)
            instance.initialize(manifest)
            self.events.publish_sync(Event(
                type=EventType.PLUGIN_LOADED,
                source="kernel",
                payload={"id": manifest["id"], "name": manifest["name"]},
            ))
        except Exception as exc:
            print(f"[AetherKernel] Plugin load failed ({plugin_path.name}): {exc}")

    def activate(self, plugin_id: str) -> bool:
        plugin = self.registry.get(plugin_id)
        if plugin is None:
            return False
        plugin.activate()
        self._active.add(plugin_id)
        self.events.publish_sync(Event(
            type=EventType.PLUGIN_ACTIVATED,
            source="kernel",
            payload={"id": plugin_id},
        ))
        return True

    def deactivate(self, plugin_id: str) -> bool:
        plugin = self.registry.get(plugin_id)
        if plugin is None or plugin_id not in self._active:
            return False
        plugin.deactivate()
        self._active.discard(plugin_id)
        self.events.publish_sync(Event(
            type=EventType.PLUGIN_DEACTIVATED,
            source="kernel",
            payload={"id": plugin_id},
        ))
        return True

    @property
    def active_plugin_ids(self) -> list[str]:
        return list(self._active)

    # ── VERATH dispatch ───────────────────────────────────────────────────

    def run_verath(
        self,
        mode: str,
        prompt: Any,
        context: dict | None = None,
    ) -> tuple[str, dict]:
        """
        Dispatch a prompt to VERATH using the named mode.

        Modes: dialogue | planner | explainer | critic
        Falls back to dialogue for unknown mode names.
        """
        ctx = context or {}
        runners = {
            "dialogue": self.verath._dialogue_mode,
            "planner":  self.verath._planner_mode,
            "explainer": self.verath._explainer_mode,
            "critic":   self.verath._critic_mode,
        }
        runner = runners.get(mode, self.verath._dialogue_mode)
        return runner(prompt, ctx)

    # ── Observability ─────────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "verath": self.verath.status(),
            "plugins": {
                "loaded": self.registry.all_ids(),
                "active": self.active_plugin_ids,
            },
        }

    # ── Async lifecycle ───────────────────────────────────────────────────

    async def start(self, auto_activate: bool = True) -> None:
        """Activate all loaded plugins and start the event loop."""
        if auto_activate:
            for pid in self.registry.all_ids():
                self.activate(pid)
        await self.events.run()

    def stop(self) -> None:
        for pid in list(self._active):
            self.deactivate(pid)
        self.events.stop()
