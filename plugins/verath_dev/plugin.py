"""VERATH Software Development Plugin — live code analysis on filesystem events."""
from __future__ import annotations
from pathlib import Path

from aetherlinkos.plugin.base import BasePlugin
from aetherlinkos.core.events import Event, EventType
from aetherlinkos.sdk.analyzer import CodeAnalyzer, AnalysisType

_CODE_EXTENSIONS: frozenset[str] = frozenset({
    ".py", ".ts", ".js", ".tsx", ".jsx",
    ".rs", ".go", ".java", ".c", ".cpp", ".cs",
})

_EXT_LANG: dict[str, str] = {
    ".py":  "python",   ".ts": "typescript", ".tsx": "typescript",
    ".js":  "javascript", ".jsx": "javascript",
    ".rs":  "rust",     ".go": "go",
    ".java": "java",    ".c": "c",   ".cpp": "cpp",  ".cs": "csharp",
}


class Plugin(BasePlugin):
    """
    Subscribes to FS_MODIFIED events and runs VERATH syntax analysis on
    any modified source file. Emits CODE_ANALYZED events with findings metadata.
    """

    def on_initialize(self) -> None:
        self._analyzer = CodeAnalyzer(self.kernel)

    def on_activate(self) -> None:
        self.kernel.events.subscribe(EventType.FS_MODIFIED, self._on_file_modified)

    def on_deactivate(self) -> None:
        self.kernel.events.unsubscribe(EventType.FS_MODIFIED, self._on_file_modified)

    async def _on_file_modified(self, event: Event) -> None:
        path = Path(event.payload.get("path", ""))
        if path.suffix not in _CODE_EXTENSIONS:
            return
        try:
            code = path.read_text(encoding="utf-8", errors="ignore")
            language = _EXT_LANG.get(path.suffix, "python")
            result = self._analyzer.analyze(code, language, AnalysisType.SYNTAX)
            await self.kernel.events.publish(Event(
                type=EventType.CODE_ANALYZED,
                source=self.plugin_id,
                payload={
                    "path":           str(path),
                    "language":       language,
                    "severity":       result.severity,
                    "findings_count": len(result.findings),
                },
            ))
        except Exception:
            pass
