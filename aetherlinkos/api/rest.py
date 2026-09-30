"""FastAPI REST interface for the AetherLink kernel and VERATH SDK."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aetherlinkos.core.kernel import AetherKernel

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    _HAS_FASTAPI = True
except ImportError:
    _HAS_FASTAPI = False


def build_app(kernel: "AetherKernel") -> "FastAPI | None":
    """
    Build and return a FastAPI application wired to the given kernel.
    Returns None when FastAPI is not installed.
    """
    if not _HAS_FASTAPI:
        return None

    app = FastAPI(
        title="AetherLinkOS API",
        description="VERATH-ΦΘ AGI Software Development and OS Plugin Framework",
        version="0.1.0",
    )

    # ── Request models ────────────────────────────────────────────────────

    class VerathRequest(BaseModel):
        text: str
        mode: str = "dialogue"
        tone: list[str] = []

    class AnalyzeRequest(BaseModel):
        code: str
        language: str = "python"
        analysis_type: str = "semantic"

    class GenerateRequest(BaseModel):
        spec: str
        language: str = "python"
        context: str = ""
        tone: list[str] = ["curious"]

    class ReviewRequest(BaseModel):
        code: str
        language: str = "python"
        context: str = ""

    # ── Kernel status ─────────────────────────────────────────────────────

    @app.get("/status", summary="Kernel and VERATH status snapshot")
    async def get_status() -> dict:
        return kernel.status()

    # ── VERATH direct access ──────────────────────────────────────────────

    @app.post("/verath/run", summary="Run a prompt through the VERATH ΦΘ loop")
    async def run_verath(req: VerathRequest) -> dict:
        prompt = {"text": req.text, "tone": req.tone, "targets": [], "metadata": {}}
        resp, state = kernel.run_verath(req.mode, prompt)
        return {
            "response":  resp,
            "aai":       state.get("aai"),
            "aai_class": state.get("aai_class"),
        }

    # ── SDK endpoints ─────────────────────────────────────────────────────

    @app.post("/sdk/analyze", summary="Analyze source code with VERATH critic mode")
    async def analyze_code(req: AnalyzeRequest) -> dict:
        from aetherlinkos.sdk.analyzer import CodeAnalyzer, AnalysisType
        try:
            atype = AnalysisType(req.analysis_type)
        except ValueError:
            atype = AnalysisType.SEMANTIC
        result = CodeAnalyzer(kernel).analyze(req.code, req.language, atype)
        return {
            "language":      result.language,
            "analysis_type": result.analysis_type.value,
            "severity":      result.severity,
            "findings":      result.findings,
            "aai":           result.verath_state.get("aai"),
        }

    @app.post("/sdk/generate", summary="Generate code from a specification")
    async def generate_code(req: GenerateRequest) -> dict:
        from aetherlinkos.sdk.generator import CodeGenerator
        result = CodeGenerator(kernel).generate(
            req.spec, req.language, context=req.context, tone=req.tone
        )
        return {
            "language": result.language,
            "code":     result.code,
            "aai":      result.verath_state.get("aai"),
        }

    @app.post("/sdk/review", summary="Review source code with VERATH critic mode")
    async def review_code(req: ReviewRequest) -> dict:
        from aetherlinkos.sdk.reviewer import CodeReviewer
        result = CodeReviewer(kernel).review(req.code, req.language, req.context)
        return {
            "approved": result.approved,
            "summary":  result.summary,
            "score":    result.score,
            "comments": [
                {"severity": c.severity, "message": c.message, "line": c.line}
                for c in result.comments
            ],
        }

    # ── Plugin management ─────────────────────────────────────────────────

    @app.get("/plugins", summary="List all loaded and active plugins")
    async def list_plugins() -> dict:
        return {
            "loaded": kernel.registry.all_ids(),
            "active": kernel.active_plugin_ids,
        }

    @app.post("/plugins/{plugin_id}/activate", summary="Activate a loaded plugin")
    async def activate_plugin(plugin_id: str) -> dict:
        if not kernel.activate(plugin_id):
            raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")
        return {"activated": plugin_id}

    @app.post("/plugins/{plugin_id}/deactivate", summary="Deactivate an active plugin")
    async def deactivate_plugin(plugin_id: str) -> dict:
        if not kernel.deactivate(plugin_id):
            raise HTTPException(
                status_code=404,
                detail=f"Plugin '{plugin_id}' not found or not active",
            )
        return {"deactivated": plugin_id}

    from aetherlinkos.api.auth import protect_app
    protect_app(app)

    return app
