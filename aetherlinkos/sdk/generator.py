"""VERATH Θ-powered code generation — dialogue mode for expressive synthesis."""
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aetherlinkos.core.kernel import AetherKernel


@dataclass
class GeneratedCode:
    language: str
    spec: str
    code: str
    verath_state: dict
    raw_response: str


class CodeGenerator:
    """
    Transforms natural-language specifications into idiomatic source code
    using VERATH dialogue mode (full ΣΦΘ expression).

    The ΦΘ loop generates ≥3 implementation branches (Φ) and converges on
    the highest-entropy safe branch (Θ), producing code that balances
    novelty with correctness.
    """

    def __init__(self, kernel: "AetherKernel") -> None:
        self._kernel = kernel

    def generate(
        self,
        spec: str,
        language: str = "python",
        context: str = "",
        tone: list[str] | None = None,
    ) -> GeneratedCode:
        ctx_note = f"\n\nContext: {context}" if context else ""
        prompt = {
            "text": (
                f"Generate {language} code for the following specification:"
                f"\n\n{spec}{ctx_note}\n\n"
                f"Requirements: clean, idiomatic {language}; proper type annotations "
                f"where applicable; no unnecessary comments."
            ),
            "tone": tone or ["curious"],
            "targets": [language, "generation"],
            "metadata": {},
        }
        response, state = self._kernel.run_verath("dialogue", prompt)
        return GeneratedCode(
            language=language,
            spec=spec,
            code=self._extract_code(response, language),
            verath_state=state,
            raw_response=response,
        )

    def generate_from_plan(
        self,
        steps: list[str],
        language: str = "python",
    ) -> list[GeneratedCode]:
        """Generate code for each step of a structured plan."""
        return [self.generate(step, language) for step in steps]

    def _extract_code(self, response: str, language: str) -> str:
        fence = f"```{language}"
        if fence in response:
            start = response.index(fence) + len(fence)
            remaining = response[start:]
            end = remaining.index("```") if "```" in remaining else len(remaining)
            return remaining[:end].strip()
        if "```" in response:
            start = response.index("```") + 3
            remaining = response[start:]
            end = remaining.index("```") if "```" in remaining else len(remaining)
            return remaining[:end].strip()
        return response
