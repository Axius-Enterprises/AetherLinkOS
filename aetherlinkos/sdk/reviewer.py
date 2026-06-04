"""VERATH-powered code review — critic mode with structured severity output."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aetherlinkos.core.kernel import AetherKernel

_ERROR_WORDS   = {"bug", "error", "critical", "security", "vulnerability", "unsafe"}
_WARNING_WORDS = {"warning", "issue", "problem", "avoid", "risky"}
_SUGGEST_WORDS = {"suggest", "consider", "improve", "prefer", "refactor"}


@dataclass
class ReviewComment:
    severity: str      # "info" | "suggestion" | "warning" | "error"
    message: str
    line: int | None = None


@dataclass
class CodeReview:
    approved: bool
    summary: str
    comments: list[ReviewComment] = field(default_factory=list)
    score: float = 0.0   # 0.0 – 1.0
    verath_state: dict = field(default_factory=dict)


class CodeReviewer:
    """
    Runs source code through VERATH critic mode (raised disdain, solemn tone)
    and parses the response into a structured CodeReview.

    The review covers correctness, anti-patterns, security, and idiomatic quality.
    Score is derived from the post-loop AAI — higher AAI correlates with a
    more rigorous review pass.
    """

    def __init__(self, kernel: "AetherKernel") -> None:
        self._kernel = kernel

    def review(
        self,
        code: str,
        language: str = "python",
        context: str = "",
    ) -> CodeReview:
        ctx_note = f"\n\nContext: {context}" if context else ""
        prompt = {
            "text": (
                f"Perform a detailed code review of this {language} code. "
                f"Identify bugs, anti-patterns, security issues, and style problems. "
                f"Rate overall quality 0.0 (unacceptable) to 1.0 (excellent).{ctx_note}\n\n"
                f"```{language}\n{code}\n```"
            ),
            "tone": ["solemn"],
            "targets": [language, "review"],
            "metadata": {},
        }
        response, state = self._kernel.run_verath("critic", prompt)
        return self._parse(response, state)

    def _parse(self, response: str, state: dict) -> CodeReview:
        lines = [l.strip() for l in response.splitlines() if l.strip()]
        comments: list[ReviewComment] = []
        blocked = "SAFETY BLOCK" in response

        for line in lines:
            if line.startswith("—"):
                continue
            lo = line.lower()
            if any(w in lo for w in _ERROR_WORDS):
                sev = "error"
            elif any(w in lo for w in _WARNING_WORDS):
                sev = "warning"
            elif any(w in lo for w in _SUGGEST_WORDS):
                sev = "suggestion"
            else:
                sev = "info"
            comments.append(ReviewComment(severity=sev, message=line))

        error_count = sum(1 for c in comments if c.severity == "error")
        approved = not blocked and error_count == 0
        score = float(state.get("aai", 0.8))
        if error_count > 0:
            score = max(0.0, score - 0.1 * error_count)

        summary = lines[0] if lines else response[:120]
        return CodeReview(
            approved=approved,
            summary=summary,
            comments=comments,
            score=round(min(max(score, 0.0), 1.0), 4),
            verath_state=state,
        )
