"""VERATH OS Integration Plugin — filesystem bridging and scheduled health checks."""
from __future__ import annotations
import platform

from aetherlinkos.plugin.base import BasePlugin
from aetherlinkos.core.events import Event, EventType
from aetherlinkos.os_hooks.scheduler import TaskScheduler


class Plugin(BasePlugin):
    """
    Bridges OS-level filesystem events to VERATH_TURN_COMPLETE notifications
    and runs a scheduled VERATH health-check every 5 minutes.

    The health check uses planner mode to produce a structured status report
    and emits it back on the event bus for any subscribers.
    """

    HEALTH_INTERVAL: float = 300.0   # 5 minutes

    def on_initialize(self) -> None:
        self._scheduler = TaskScheduler()
        self._platform = platform.system()

    def on_activate(self) -> None:
        self.kernel.events.subscribe(EventType.FS_CREATED, self._on_fs_event)
        self.kernel.events.subscribe(EventType.FS_DELETED, self._on_fs_event)
        self._scheduler.register(
            name="verath_health",
            interval=self.HEALTH_INTERVAL,
            callback=self._health_check,
        )

    def on_deactivate(self) -> None:
        self.kernel.events.unsubscribe(EventType.FS_CREATED, self._on_fs_event)
        self.kernel.events.unsubscribe(EventType.FS_DELETED, self._on_fs_event)
        self._scheduler.stop()

    async def _on_fs_event(self, event: Event) -> None:
        await self.kernel.events.publish(Event(
            type=EventType.VERATH_TURN_COMPLETE,
            source=self.plugin_id,
            payload={
                "trigger":  event.type.name,
                "path":     event.payload.get("path", ""),
                "platform": self._platform,
            },
        ))

    async def _health_check(self) -> None:
        prompt = {
            "text":     "Report current system health status and Axionic Ascension Index.",
            "tone":     ["curious"],
            "targets":  ["health", "aai"],
            "metadata": {},
        }
        _, state = self.kernel.run_verath("planner", prompt)
        await self.kernel.events.publish(Event(
            type=EventType.VERATH_TURN_COMPLETE,
            source=self.plugin_id,
            payload={
                "health_check": True,
                "aai":          state.get("aai"),
                "aai_class":    state.get("aai_class"),
                "platform":     self._platform,
            },
        ))
