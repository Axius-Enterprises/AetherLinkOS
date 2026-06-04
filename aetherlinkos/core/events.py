"""Async event bus — OS, plugin, VERATH, and SDK events."""
from __future__ import annotations
import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Awaitable


class EventType(Enum):
    # Filesystem events
    FS_CREATED  = auto()
    FS_MODIFIED = auto()
    FS_DELETED  = auto()
    FS_MOVED    = auto()
    # Process events
    PROCESS_STARTED = auto()
    PROCESS_ENDED   = auto()
    # Scheduler events
    SCHEDULED_TASK = auto()
    # Plugin lifecycle
    PLUGIN_LOADED      = auto()
    PLUGIN_ACTIVATED   = auto()
    PLUGIN_DEACTIVATED = auto()
    # VERATH runtime
    VERATH_TURN_COMPLETE = auto()
    VERATH_SAFETY_BLOCK  = auto()
    VERATH_EKPYROTIC     = auto()
    # SDK
    CODE_ANALYZED  = auto()
    CODE_GENERATED = auto()
    CODE_REVIEWED  = auto()


@dataclass
class Event:
    type: EventType
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


Handler = Callable[[Event], Awaitable[None]]


class EventBus:
    """Async publish/subscribe event bus for the AetherLink kernel."""

    def __init__(self) -> None:
        self._handlers: dict[EventType, list[Handler]] = defaultdict(list)
        self._queue: asyncio.Queue[Event] = asyncio.Queue()
        self._running = False

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Handler) -> None:
        handlers = self._handlers[event_type]
        if handler in handlers:
            handlers.remove(handler)

    async def publish(self, event: Event) -> None:
        await self._queue.put(event)

    def publish_sync(self, event: Event) -> None:
        """Thread-safe synchronous publish; silently drops if no running loop."""
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(self._queue.put_nowait, event)
        except RuntimeError:
            pass

    async def run(self) -> None:
        self._running = True
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=0.1)
                for handler in list(self._handlers.get(event.type, [])):
                    try:
                        await handler(event)
                    except Exception:
                        pass
                self._queue.task_done()
            except asyncio.TimeoutError:
                pass

    def stop(self) -> None:
        self._running = False
