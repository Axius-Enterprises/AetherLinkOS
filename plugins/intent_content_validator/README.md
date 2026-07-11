# Intent Content Consistency Validator Plugin

A plugin that integrates the `@intentsolutionsio/000-jeremy-content-consistency-validator` npm package into AetherLinkOS.

## Overview

This plugin:
- Manages a Node.js wrapper service that exposes the intent validator
- Provides async validation methods for content consistency checking
- Handles service lifecycle (startup/shutdown) automatically
- Bridges between the Python kernel and Node.js validator runtime

## Architecture

```
AetherLinkOS Kernel
        ↓
  Python Plugin (plugin.py)
        ↓
  HTTP Client (httpx)
        ↓
  Node.js Service (../intent_content_validator_js/)
        ↓
  @intentsolutionsio/000-jeremy-content-consistency-validator
```

## Installation

The plugin is auto-discovered by AetherLinkOS's plugin registry.

Node.js dependencies are installed via pnpm:

```bash
cd ../intent_content_validator_js/
pnpm install
```

## Usage

### As a Plugin (AetherLinkOS)

```python
from aetherlinkos.core.kernel import AetherKernel

kernel = AetherKernel()
# Plugin auto-loads from registry

# Activate plugin
kernel.activate_plugin("intent-content-validator")

# Get plugin instance
plugin = kernel.registry.get("intent-content-validator")

# Validate content
result = await plugin.validate("Check this content")
print(result)
```

### Direct Plugin Usage

```python
from plugins.intent_content_validator.plugin import Plugin
from aetherlinkos.core.kernel import AetherKernel

kernel = AetherKernel()
plugin = Plugin(plugin_id="intent-content-validator", kernel=kernel)

# Initialize and activate
plugin.on_initialize()
plugin.on_activate()  # Starts Node.js service

# Validate single content
result = await plugin.validate("Content to check")

# Validate batch
results = await plugin.validate_batch(["Content 1", "Content 2", "Content 3"])

# Clean shutdown
plugin.on_deactivate()  # Stops Node.js service
```

## Plugin Methods

### `validate(content: str, options: dict | None = None) -> dict`

Validate a single content string for consistency.

**Parameters:**
- `content` (str): The text content to validate
- `options` (dict, optional): Validator-specific options

**Returns:** Dictionary with validation result

**Example:**
```python
result = await plugin.validate("Check this for consistency")
# {
#   "success": true,
#   "data": {
#     "valid": true,
#     "issues": []
#   }
# }
```

### `validate_batch(contents: list[str], options: dict | None = None) -> dict`

Validate multiple content strings in batch.

**Parameters:**
- `contents` (list[str]): List of text contents to validate
- `options` (dict, optional): Validator-specific options

**Returns:** Dictionary with batch validation results

**Example:**
```python
results = await plugin.validate_batch(["Content 1", "Content 2"])
# {
#   "success": true,
#   "data": [
#     {"valid": true, "issues": []},
#     {"valid": false, "issues": ["Issue 1", "Issue 2"]}
#   ]
# }
```

## Service Configuration

The Node.js service runs on `http://127.0.0.1:3001` by default.

To configure a different port, set the `SERVICE_PORT` and `SERVICE_HOST` class attributes or environment variable:

```python
plugin.SERVICE_PORT = 3002
plugin.SERVICE_HOST = "0.0.0.0"
```

## Lifecycle Events

The plugin publishes events on activation/deactivation:

```python
plugin.on_activate()
# Publishes: Event(
#   type=EventType.PLUGIN_ACTIVATED,
#   source="intent-content-validator",
#   payload={
#     "message": "Intent Content Validator service started",
#     "service_url": "http://127.0.0.1:3001"
#   }
# )
```

## Error Handling

The plugin raises `RuntimeError` if:
- Service fails to start
- HTTP requests timeout (10s default)
- Validation request fails
- Service is accessed before ready

Example:

```python
try:
    result = await plugin.validate("content")
except RuntimeError as e:
    print(f"Validation error: {e}")
```

## Configuration

Extend `config/aetherlinkos.toml` to configure the plugin:

```toml
[plugins.intent-content-validator]
enabled = true
service_port = 3001
service_host = "127.0.0.1"
service_timeout = 10.0
```

## Testing

Run unit tests:

```bash
pytest tests/test_intent_validator_plugin.py -v
```

Run with coverage:

```bash
pytest tests/test_intent_validator_plugin.py --cov=plugins.intent_content_validator
```

## Troubleshooting

### Service won't start

Check that Node.js is installed and pnpm dependencies are available:

```bash
cd ../intent_content_validator_js/
pnpm install
node src/index.js  # Test manual start
```

### HTTP connection timeout

Check service is running and accessible:

```bash
curl http://127.0.0.1:3001/health
```

### Port already in use

Change `SERVICE_PORT` or kill existing process on that port.

## License

MIT

## Contributing

See main AetherLinkOS CONTRIBUTING.md guidelines.
