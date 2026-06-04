"""Abstract base class for all AetherLinkOS plugins."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aetherlinkos.core.kernel import AetherKernel


class BasePlugin(ABC):
    """
    All AetherLinkOS plugins inherit from this class.

    Lifecycle:
        initialize(manifest)  — called once on load; stores manifest
        activate()            — called when the kernel activates the plugin
        deactivate()          — called on deactivation or kernel shutdown
    """

    def __init__(self, kernel: "AetherKernel") -> None:
        self.kernel = kernel
        self.manifest: dict = {}

    def initialize(self, manifest: dict) -> None:
        self.manifest = manifest
        self.on_initialize()

    def activate(self) -> None:
        self.on_activate()

    def deactivate(self) -> None:
        self.on_deactivate()

    @abstractmethod
    def on_initialize(self) -> None:
        """Called once when the plugin is first loaded by the registry."""

    @abstractmethod
    def on_activate(self) -> None:
        """Called each time the plugin is activated by the kernel."""

    @abstractmethod
    def on_deactivate(self) -> None:
        """Called when the plugin is deactivated or the kernel shuts down."""

    @property
    def plugin_id(self) -> str:
        return self.manifest.get("id", "unknown")

    @property
    def plugin_name(self) -> str:
        return self.manifest.get("name", "Unknown Plugin")

    @property
    def plugin_version(self) -> str:
        return self.manifest.get("version", "0.0.0")
