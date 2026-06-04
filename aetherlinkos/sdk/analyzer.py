"""VERATH Φ-powered code analysis — runs critic mode against source code."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aetherlinkos.core.kernel import AetherKernel


class AnalysisType(str, Enum):
    SYNTAX     = "syntax"
    SEMANTIC   = "semantic"
    SECURITY   = "security"
    COMPLEXITY = "complexity"
    STYLE      = "style"


@dataclass
class AnalysisResult:
    language: str
    analysis_type: AnalysisType
    findings: list[str]
    severity: str      # "info" | "warning" | "critical"
    verath_state: dict
    raw_response: str


_SEVERITY: dict[str, str] = {
    "security":   "critical",
    "syntax":     "critical",
    "complexity": "warning",
    "semantic":   "warning",
    "style":      "info",
}


class CodeAnalyzer:
    """
    Routes source code through VERATH critic mode to produce structured findings.

    Each analysis type maps to a different adversarial lens:
      security   → VERATH scans for exploit surfaces and unsafe patterns
      syntax     → structural correctness under strict disdain
      semantic   → logical coherence and intent alignment
      complexity → cognitive load, cyclomatic depth, abstraction misuse
      style      → readability, naming, idiomatic compliance
    """

    def __init__(self, kernel: "AetherKernel") -> None:
        self._kernel = kernel

    def analyze(
        self,
        code: str,
        language: str = "python",
        analysis_type: AnalysisType = AnalysisType.SEMANTIC,
    ) -> AnalysisResult:
        prompt = {
            "text": (
                f"Analyze this {language} code for {analysis_type.value} issues. "
                f"Provide specific findings, line-level observations, and actionable "
                f"recommendations. Be precise and adversarial.\n\n"
                f"```{language}\n{code}\n```"
            ),
            "tone": ["solemn"],
            "targets": [language, analysis_type.value],
            "metadata": {},
        }
        response, state = self._kernel.run_verath("critic", prompt)
        return AnalysisResult(
            language=language,
            analysis_type=analysis_type,
            findings=self._extract_findings(response),
            severity=_SEVERITY.get(analysis_type.value, "info"),
            verath_state=state,
            raw_response=response,
        )

    def analyze_multi(
        self,
        code: str,
        language: str = "python",
        types: list[AnalysisType] | None = None,
    ) -> list[AnalysisResult]:
        """Run all (or selected) analysis types against the same code snippet."""
        return [self.analyze(code, language, t) for t in (types or list(AnalysisType))]

    def _extract_findings(self, response: str) -> list[str]:
        return [
            line.strip()
            for line in response.splitlines()
            if line.strip() and not line.strip().startswith("—")
        ]
