# Intent Content Consistency Validator Service

A Node.js HTTP wrapper around the `@intentsolutionsio/000-jeremy-content-consistency-validator` package.

## Installation

```bash
cd plugins/intent_content_validator_js
pnpm install
```

## Running

Start the service:

```bash
pnpm start
```

The service will listen on `http://127.0.0.1:3001` by default. Override with `PORT` environment variable:

```bash
PORT=3002 pnpm start
```

## API Endpoints

### Health Check
```
GET /health
```
Returns service status.

### Validate Single Content
```
POST /validate
Content-Type: application/json

{
  "content": "Text to validate",
  "options": {}
}
```

### Validate Batch
```
POST /validate-batch
Content-Type: application/json

{
  "contents": ["Text 1", "Text 2"],
  "options": {}
}
```

### Get Configuration
```
GET /config
```
Returns service configuration and endpoint information.

## Usage from Python

The Python plugin (`../intent_content_validator/plugin.py`) manages this service lifecycle:

```python
from plugins.intent_content_validator.plugin import Plugin

# Create plugin
plugin = Plugin(plugin_id="intent-content-validator", kernel=kernel)

# Activate (starts service)
plugin.on_activate()

# Validate content
result = await plugin.validate("Some content to check")

# Deactivate (stops service)
plugin.on_deactivate()
```

## Development

Watch mode (requires `--watch` flag):

```bash
pnpm dev
```

## Environment

- **Node.js**: >= 18.0.0
- **Package Manager**: pnpm

## License

MIT
