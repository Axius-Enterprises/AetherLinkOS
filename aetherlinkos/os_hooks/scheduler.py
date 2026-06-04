"""Async periodic task scheduler for AetherLinkOS plugins."""
from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass, field
from typing import Callable, Awaitable


@dataclass
class ScheduledTask:
    name: str
    interval: float   # seconds between executions
    callback: Callable[[], Awaitable[None]]
    last_run: float = field(default_factory=time.time)
    enabled: bool = True


class TaskScheduler:
    """
    Registers async callbacks and fires them at configurable intervals.

    Designed to run concurrently with the AetherLink event bus via asyncio.
    Plugins register tasks in on_activate() and unregister in on_deactivate().
    """

    _TICK: float = 0.5  # internal poll interval

    def __init__(self) -> None:
        self._tasks: dict[str, ScheduledTask] = {}
        self._running = False

    def register(
        self,
        name: str,
        interval: float,
        callback: Callable[[], Awaitable[None]],
    ) -> None:
        self._tasks[name] = ScheduledTask(
            name=name, interval=interval, callback=callback
        )

    def unregister(self, name: str) -> None:
        self._tasks.pop(name, None)

    def enable(self, name: str) -> None:
        if name in self._tasks:
            self._tasks[name].enabled = True

    def disable(self, name: str) -> None:
        if name in self._tasks:
            self._tasks[name].enabled = False

    def task_names(self) -> list[str]:
        return list(self._tasks.keys())

    async def run(self) -> None:
        self._running = True
        while self._running:
            now = time.time()
            for task in list(self._tasks.values()):
                if task.enabled and now - task.last_run >= task.interval:
                    task.last_run = now
                    try:
                        await task.callback()
                    except Exception:
                        pass
            await asyncio.sleep(self._TICK)

    def stop(self) -> None:
        self._running = False
