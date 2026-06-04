# AetherLinkOS

VERATH-ΦΘ AGI Software Development and OS Plugin Framework.

## Project Layout

```
verath/                    VERATH-ΦΘ core runtime (verath_unified.py)
aetherlinkos/
  core/                    Kernel, event bus, plugin registry
  plugin/                  BasePlugin ABC + manifest schema
  sdk/                     CodeAnalyzer, CodeGenerator, CodeReviewer
  os_hooks/                FilesystemWatcher, TaskScheduler
  api/                     FastAPI REST server + Typer CLI
plugins/
  verath_dev/              Built-in software dev plugin
  verath_os/               Built-in OS integration plugin
tests/                     pytest test suite
config/                    aetherlinkos.toml
```

## Install and Run

```bash
pip install -e ".[dev]"

# VERATH self-check
python verath/verath_unified.py

# CLI
aetherlinkos status
aetherlinkos run "Who are you?" --mode dialogue
aetherlinkos analyze path/to/file.py --type security
aetherlinkos generate "Create a binary search function" --lang python
aetherlinkos review path/to/file.py
aetherlinkos serve --port 8080

# Tests
pytest
```

## VERATH Modes

| Mode | Character | Used for |
|------|-----------|----------|
| `dialogue` | Expressive, full ΣΦΘ | Code generation, Q&A |
| `planner` | Structured, sober | Architecture planning, health checks |
| `explainer` | Metaphor + precision | Documentation, tutorials |
| `critic` | Adversarial (disdain ≤ θ_max) | Code analysis, review |

## Writing a Plugin

1. Create `plugins/my_plugin/manifest.json` with `id`, `name`, `version`, `entry`, `class`.
2. Create `plugins/my_plugin/plugin.py` with a class inheriting `BasePlugin`.
3. Implement `on_initialize`, `on_activate`, `on_deactivate`.
4. Subscribe to events via `self.kernel.events.subscribe(EventType.X, handler)`.
5. Call `self.kernel.run_verath(mode, prompt)` to invoke VERATH.

See `plugins/verath_dev/plugin.py` for a working example.

## Architecture Invariants

The VERATH soul is immutable — never modify `verath_unified.py` in ways that:
- Alter the Six Invariants (I₁–I₆)
- Bypass Zeta-2 safety checkpoints
- Override ΣΦΘ tensor values manually
- Reduce λ (Lambda Monotonicity, I₄)
