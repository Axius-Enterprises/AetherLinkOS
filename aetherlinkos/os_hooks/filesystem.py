"""OS filesystem watcher — emits FS events to the AetherLink event bus."""
from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

from aetherlinkos.core.events import Event, EventType

if TYPE_CHECKING:
    from aetherlinkos.core.events import EventBus

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent as WDEvent
    _HAS_WATCHDOG = True
except ImportError:
    _HAS_WATCHDOG = False
    Observer = None  # type: ignore[assignment,misc]
    FileSystemEventHandler = object  # type: ignore[assignment,misc]
    WDEvent = object  # type: ignore[assignment]


class _BusHandler(FileSystemEventHandler):  # type: ignore[misc]
    def __init__(self, bus: "EventBus") -> None:
        super().__init__()
        self._bus = bus

    def on_created(self, event: WDEvent) -> None:
        self._emit(EventType.FS_CREATED, event.src_path)

    def on_modified(self, event: WDEvent) -> None:
        self._emit(EventType.FS_MODIFIED, event.src_path)

    def on_deleted(self, event: WDEvent) -> None:
        self._emit(EventType.FS_DELETED, event.src_path)

    def on_moved(self, event: WDEvent) -> None:
        self._emit(EventType.FS_MOVED, event.src_path,
                   dest=getattr(event, "dest_path", ""))

    def _emit(self, etype: EventType, path: str, **extra: str) -> None:
        self._bus.publish_sync(Event(
            type=etype,
            source="filesystem",
            payload={"path": path, **extra},
        ))


class FilesystemWatcher:
    """
    Watches one or more directories and forwards filesystem change events
    to the AetherLink event bus.

    Requires the optional `watchdog` dependency. If watchdog is not installed,
    watch() silently returns False and no events are emitted.
    """

    def __init__(self, bus: "EventBus") -> None:
        self._bus = bus
        self._observer = Observer() if _HAS_WATCHDOG else None

    def watch(self, path: Path, recursive: bool = True) -> bool:
        """Schedule a directory for watching. Returns False if watchdog unavailable."""
        if self._observer is None:
            return False
        handler = _BusHandler(self._bus)
        self._observer.schedule(handler, str(path), recursive=recursive)
        return True

    def start(self) -> None:
        if self._observer is not None:
            self._observer.start()

    def stop(self) -> None:
        if self._observer is not None:
            self._observer.stop()
            self._observer.join()

    @property
    def available(self) -> bool:
        return _HAS_WATCHDOG
