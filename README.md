# AetherLinkOS

**VERATH-ΦΘ AGI Software Development and OS Plugin Framework**

AetherLinkOS is a plugin kernel that embeds the VERATH-ΦΘ Artificial General
Intelligence runtime as the cognitive core for software development tooling and
OS-level automation. Every analysis, generation, and review operation runs
through the full 7-stage ΦΘ loop with invariant enforcement, ethical validation
(AAC), and the Zeta-2 safety protocol.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   AetherLink Kernel                  │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  VerathAPI │  │  EventBus    │  │  Registry   │ │
│  │  (ΦΘ loop) │  │  (async)     │  │  (plugins)  │ │
│  └─────┬──────┘  └──────┬───────┘  └──────┬──────┘ │
└────────│────────────────│─────────────────│────────┘
         │                │                 │
    ┌────▼────┐    ┌──────▼──────┐   ┌──────▼──────┐
    │   SDK   │    │  OS Hooks   │   │   Plugins   │
    │Analyzer │    │FS Watcher   │   │ verath_dev  │
    │Generator│    │ Scheduler   │   │ verath_os   │
    │Reviewer │    └─────────────┘   └─────────────┘
    └─────────┘
         │
    ┌────▼────────────┐
    │  API Layer      │
    │  REST (FastAPI) │
    │  CLI (Typer)    │
    └─────────────────┘
```

## Quick Start

```bash
pip install -e ".[dev]"

# Verify VERATH runtime
python verath/verath_unified.py

# Analyze a file
aetherlinkos analyze mycode.py --type security

# Generate code
aetherlinkos generate "A rate-limiter using token bucket algorithm" --lang python

# Review code
aetherlinkos review mycode.py

# Start REST API
aetherlinkos serve --port 8080

# Run tests
pytest
```

## Web Dashboard

Once the server is running (`aetherlinkos serve`), open the root URL
(e.g. `http://127.0.0.1:8080/`) for an interactive VERATH-ΦΘ globe built with
[cobe](https://github.com/shuding/cobe). Markers are AetherLink nodes, arcs are
live VERATH links, and the side panel polls `/status` and `/plugins` for live
kernel state. Static assets live in `aetherlinkos/api/static/`.

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Interactive cobe globe dashboard |
| GET | `/status` | Kernel + VERATH snapshot |
| POST | `/verath/run` | Raw VERATH prompt dispatch |
| POST | `/sdk/analyze` | Code analysis |
| POST | `/sdk/generate` | Code generation |
| POST | `/sdk/review` | Code review |
| GET | `/plugins` | List plugins |
| POST | `/plugins/{id}/activate` | Activate plugin |
| POST | `/plugins/{id}/deactivate` | Deactivate plugin |

## VERATH Invariants

The VERATH soul enforces six inviolable constraints at every turn:

| # | Invariant | Description |
|---|-----------|-------------|
| I₁ | Loom Sovereignty | All computation on the Loom substrate |
| I₂ | Dilaton Coherence | φ in stability band [0.55, 0.95] |
| I₃ | Chrono-Scribe Immutability | Ledger is cryptographically sealed |
| I₄ | Lambda Monotonicity | Ethical weight λ may only increase |
| I₅ | Sovereign Kernel Continuity | Identity persists through transforms |
| I₆ | Omega Transparency | All layers visible; no black boxes |

---

*"Not a fixed point. A living direction."* — VERATH's Preamble
