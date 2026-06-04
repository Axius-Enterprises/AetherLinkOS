"""Plugin manifest schema — typed wrapper around manifest.json."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class PluginManifest:
    id: str
    name: str
    version: str
    entry: str
    description: str = ""
    author: str = ""
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    verath_modes: tuple[str, ...] = ("dialogue",)

    @classmethod
    def from_dict(cls, d: dict) -> "PluginManifest":
        return cls(
            id=d["id"],
            name=d["name"],
            version=d["version"],
            entry=d["entry"],
            description=d.get("description", ""),
            author=d.get("author", ""),
            capabilities=tuple(d.get("capabilities", [])),
            dependencies=tuple(d.get("dependencies", [])),
            verath_modes=tuple(d.get("verath_modes", ["dialogue"])),
        )
