"""Unit tests — CodeAnalyzer, CodeGenerator, CodeReviewer SDK tools."""
from __future__ import annotations
import pytest
from aetherlinkos.core.kernel import AetherKernel
from aetherlinkos.sdk.analyzer import CodeAnalyzer, AnalysisType, AnalysisResult
from aetherlinkos.sdk.generator import CodeGenerator, GeneratedCode
from aetherlinkos.sdk.reviewer import CodeReviewer, CodeReview

_SAMPLE_PY = """
def add(a: int, b: int) -> int:
    return a + b

result = add(1, 2)
print(result)
"""

_SAMPLE_TS = """
function greet(name: string): string {
    return `Hello, ${name}!`;
}
console.log(greet("world"));
"""


@pytest.fixture(scope="module")
def kernel() -> AetherKernel:
    return AetherKernel()


# ── Analyzer ──────────────────────────────────────────────────────────────

def test_analyzer_returns_result(kernel: AetherKernel) -> None:
    result = CodeAnalyzer(kernel).analyze(_SAMPLE_PY, "python", AnalysisType.SEMANTIC)
    assert isinstance(result, AnalysisResult)
    assert result.language == "python"
    assert result.analysis_type == AnalysisType.SEMANTIC
    assert isinstance(result.findings, list)
    assert result.severity in ("info", "warning", "critical")


def test_analyzer_all_types(kernel: AetherKernel) -> None:
    results = CodeAnalyzer(kernel).analyze_multi(_SAMPLE_PY, "python")
    assert len(results) == len(list(AnalysisType))
    for r in results:
        assert isinstance(r.findings, list)
        assert r.severity in ("info", "warning", "critical")


def test_analyzer_security_is_critical(kernel: AetherKernel) -> None:
    result = CodeAnalyzer(kernel).analyze(_SAMPLE_PY, "python", AnalysisType.SECURITY)
    assert result.severity == "critical"


def test_analyzer_style_is_info(kernel: AetherKernel) -> None:
    result = CodeAnalyzer(kernel).analyze(_SAMPLE_PY, "python", AnalysisType.STYLE)
    assert result.severity == "info"


def test_analyzer_typescript(kernel: AetherKernel) -> None:
    result = CodeAnalyzer(kernel).analyze(_SAMPLE_TS, "typescript", AnalysisType.SYNTAX)
    assert result.language == "typescript"


# ── Generator ─────────────────────────────────────────────────────────────

def test_generator_returns_result(kernel: AetherKernel) -> None:
    result = CodeGenerator(kernel).generate(
        "Create a function that reverses a string", "python"
    )
    assert isinstance(result, GeneratedCode)
    assert result.language == "python"
    assert isinstance(result.code, str)
    assert len(result.code) > 0


def test_generator_with_context(kernel: AetherKernel) -> None:
    result = CodeGenerator(kernel).generate(
        "Create a Fibonacci function",
        "python",
        context="Must be iterative, not recursive.",
    )
    assert isinstance(result.code, str)


def test_generator_from_plan(kernel: AetherKernel) -> None:
    plan = [
        "Create a Stack class with push and pop methods",
        "Add a peek method to the Stack",
    ]
    results = CodeGenerator(kernel).generate_from_plan(plan, "python")
    assert len(results) == 2
    for r in results:
        assert isinstance(r.code, str)


# ── Reviewer ──────────────────────────────────────────────────────────────

def test_reviewer_returns_review(kernel: AetherKernel) -> None:
    result = CodeReviewer(kernel).review(_SAMPLE_PY, "python")
    assert isinstance(result, CodeReview)
    assert isinstance(result.approved, bool)
    assert 0.0 <= result.score <= 1.0
    assert isinstance(result.comments, list)


def test_reviewer_summary_is_string(kernel: AetherKernel) -> None:
    result = CodeReviewer(kernel).review(_SAMPLE_PY, "python")
    assert isinstance(result.summary, str) and len(result.summary) > 0


def test_reviewer_with_context(kernel: AetherKernel) -> None:
    result = CodeReviewer(kernel).review(
        _SAMPLE_PY, "python", context="Part of a public API."
    )
    assert isinstance(result, CodeReview)


def test_reviewer_comment_severities(kernel: AetherKernel) -> None:
    result = CodeReviewer(kernel).review(_SAMPLE_PY, "python")
    valid_severities = {"info", "suggestion", "warning", "error"}
    for c in result.comments:
        assert c.severity in valid_severities


def test_reviewer_typescript(kernel: AetherKernel) -> None:
    result = CodeReviewer(kernel).review(_SAMPLE_TS, "typescript")
    assert isinstance(result, CodeReview)
