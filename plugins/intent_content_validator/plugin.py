"""Intent Content Consistency Validator Plugin — bridges Node.js validator service."""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from aetherlinkos.plugin.base import BasePlugin
from aetherlinkos.core.events import Event, EventType


class Plugin(BasePlugin):
    """
    Manages Node.js content validator service and exposes validation capabilities
    to AetherLinkOS. Starts/stops service lifecycle and proxies validation requests.
    """

    SERVICE_PORT: int = 3001
    SERVICE_HOST: str = "127.0.0.1"
    SERVICE_URL: str = f"http://{SERVICE_HOST}:{SERVICE_PORT}"
    SERVICE_TIMEOUT: float = 10.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service_process: Optional[subprocess.Popen] = None
        self._http_client: Optional[httpx.AsyncClient] = None
        self._service_ready = False

    def on_initialize(self) -> None:
        """Initialize plugin configuration and state."""
        self._service_process = None
        self._http_client = None
        self._service_ready = False

    def on_activate(self) -> None:
        """Start Node.js validator service and prepare for validation requests."""
        asyncio.create_task(self._startup_service())
        self.kernel.events.subscribe(EventType.PLUGIN_ACTIVATED, self._on_plugin_event)

    def on_deactivate(self) -> None:
        """Gracefully shutdown Node.js validator service."""
        asyncio.create_task(self._shutdown_service())
        self.kernel.events.unsubscribe(EventType.PLUGIN_ACTIVATED, self._on_plugin_event)

    async def _startup_service(self) -> None:
        """Start Node.js validator service."""
        try:
            service_dir = Path(__file__).parent.parent / "intent_content_validator_js"

            if not service_dir.exists():
                raise RuntimeError(f"Service directory not found: {service_dir}")

            # Start Node.js service
            self._service_process = subprocess.Popen(
                ["node", "src/index.js"],
                cwd=service_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Initialize HTTP client
            self._http_client = httpx.AsyncClient(timeout=self.SERVICE_TIMEOUT)

            # Wait for service to be ready
            await self._wait_for_service()
            self._service_ready = True

            await self.kernel.events.publish(Event(
                type=EventType.PLUGIN_ACTIVATED,
                source=self.plugin_id,
                payload={
                    "message": "Intent Content Validator service started",
                    "service_url": self.SERVICE_URL,
                },
            ))
        except Exception as e:
            await self.kernel.events.publish(Event(
                type=EventType.PLUGIN_ACTIVATED,
                source=self.plugin_id,
                payload={
                    "error": f"Failed to start validator service: {str(e)}",
                },
            ))

    async def _shutdown_service(self) -> None:
        """Gracefully shutdown Node.js validator service."""
        try:
            if self._http_client:
                await self._http_client.aclose()

            if self._service_process:
                self._service_process.terminate()
                try:
                    self._service_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._service_process.kill()

            self._service_ready = False
        except Exception as e:
            print(f"Error during service shutdown: {e}")

    async def _wait_for_service(self, max_retries: int = 30, delay: float = 0.5) -> None:
        """Poll service health endpoint until it's ready."""
        for attempt in range(max_retries):
            try:
                response = await self._http_client.get(
                    f"{self.SERVICE_URL}/health",
                    timeout=2.0,
                )
                if response.status_code == 200:
                    return
            except Exception:
                pass

            if attempt < max_retries - 1:
                await asyncio.sleep(delay)

        raise RuntimeError(
            f"Service did not become ready after {max_retries * delay} seconds"
        )

    async def validate(self, content: str, options: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Validate content for consistency.

        Args:
            content: Text content to validate
            options: Optional validation parameters

        Returns:
            Validation result dictionary
        """
        if not self._service_ready or not self._http_client:
            raise RuntimeError("Validator service is not ready")

        payload = {
            "content": content,
            "options": options or {},
        }

        response = await self._http_client.post(
            f"{self.SERVICE_URL}/validate",
            json=payload,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Validation failed with status {response.status_code}: "
                f"{response.text}"
            )

        return response.json()

    async def validate_batch(
        self,
        contents: list,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """
        Validate multiple contents in batch.

        Args:
            contents: List of text contents to validate
            options: Optional validation parameters

        Returns:
            Batch validation result dictionary
        """
        if not self._service_ready or not self._http_client:
            raise RuntimeError("Validator service is not ready")

        payload = {
            "contents": contents,
            "options": options or {},
        }

        response = await self._http_client.post(
            f"{self.SERVICE_URL}/validate-batch",
            json=payload,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Batch validation failed with status {response.status_code}: "
                f"{response.text}"
            )

        return response.json()

    async def _on_plugin_event(self, event: Event) -> None:
        """Handle plugin lifecycle events."""
        # Placeholder for event handling logic
        pass
