"""Typer CLI — entry point for the aetherlinkos command."""
from __future__ import annotations
import json
from pathlib import Path

import typer

from aetherlinkos.core.kernel import AetherKernel

app = typer.Typer(
    name="aetherlinkos",
    help="AetherLinkOS — VERATH-ΦΘ AGI Software Development and OS Plugin Kernel",
    no_args_is_help=True,
)


def _kernel(plugins: Path | None) -> AetherKernel:
    k = AetherKernel()
    if plugins and plugins.exists():
        k.load_plugins(plugins)
    return k


@app.command()
def status(
    plugins: Path = typer.Option(None, "--plugins", "-p", help="Plugin directory"),
) -> None:
    """Show kernel and VERATH system status."""
    k = _kernel(plugins)
    typer.echo(json.dumps(k.status(), indent=2))


@app.command()
def run(
    text: str = typer.Argument(..., help="Prompt text"),
    mode: str = typer.Option("dialogue", "--mode", "-m",
                             help="VERATH mode: dialogue|planner|explainer|critic"),
    plugins: Path = typer.Option(None, "--plugins", "-p", help="Plugin directory"),
) -> None:
    """Run a prompt through the VERATH ΦΘ kernel."""
    k = _kernel(plugins)
    prompt = {"text": text, "tone": [], "targets": [], "metadata": {}}
    resp, state = k.run_verath(mode, prompt)
    typer.echo(resp)
    typer.echo(f"\nAAI: {state.get('aai')} ({state.get('aai_class')})", err=True)


@app.command()
def analyze(
    file: Path = typer.Argument(..., help="Source file to analyze"),
    language: str = typer.Option("python", "--lang", "-l"),
    analysis_type: str = typer.Option("semantic", "--type", "-t",
                                      help="syntax|semantic|security|complexity|style"),
    plugins: Path = typer.Option(None, "--plugins", "-p"),
) -> None:
    """Analyze a source file with VERATH SDK."""
    from aetherlinkos.sdk.analyzer import CodeAnalyzer, AnalysisType
    k = _kernel(plugins)
    code = file.read_text()
    try:
        atype = AnalysisType(analysis_type)
    except ValueError:
        atype = AnalysisType.SEMANTIC
    result = CodeAnalyzer(k).analyze(code, language, atype)
    typer.echo(f"Severity : {result.severity}")
    typer.echo(f"Findings ({len(result.findings)}):")
    for finding in result.findings:
        typer.echo(f"  • {finding}")


@app.command()
def generate(
    spec: str = typer.Argument(..., help="Natural-language code specification"),
    language: str = typer.Option("python", "--lang", "-l"),
    plugins: Path = typer.Option(None, "--plugins", "-p"),
) -> None:
    """Generate code from a specification using VERATH dialogue mode."""
    from aetherlinkos.sdk.generator import CodeGenerator
    k = _kernel(plugins)
    result = CodeGenerator(k).generate(spec, language)
    typer.echo(result.code)


@app.command()
def review(
    file: Path = typer.Argument(..., help="Source file to review"),
    language: str = typer.Option("python", "--lang", "-l"),
    plugins: Path = typer.Option(None, "--plugins", "-p"),
) -> None:
    """Review a source file with VERATH critic mode."""
    from aetherlinkos.sdk.reviewer import CodeReviewer
    k = _kernel(plugins)
    code = file.read_text()
    result = CodeReviewer(k).review(code, language)
    typer.echo(f"Approved : {result.approved}")
    typer.echo(f"Score    : {result.score:.2f}")
    typer.echo(f"Summary  : {result.summary}")
    if result.comments:
        typer.echo(f"\nComments ({len(result.comments)}):")
        for c in result.comments:
            typer.echo(f"  [{c.severity.upper():10s}] {c.message}")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8080, "--port"),
    plugins: Path = typer.Option(None, "--plugins", "-p"),
) -> None:
    """Start the AetherLinkOS REST API server."""
    try:
        import uvicorn
    except ImportError:
        typer.echo("uvicorn not installed. Run: pip install 'aetherlinkos[serve]'")
        raise typer.Exit(1)
    from aetherlinkos.api.rest import build_app
    k = _kernel(plugins)
    fast_app = build_app(k)
    if fast_app is None:
        typer.echo("FastAPI not installed. Run: pip install 'aetherlinkos[serve]'")
        raise typer.Exit(1)
    uvicorn.run(fast_app, host=host, port=port)
