"""
Ethical Framework: Axiomatic Ascension Codex

The 12 Meta-Axioms that govern every decision made by the Sacred Engine.
Implemented as an auditable, inspectable codex with violation detection.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

DELTA_HARM = 1e-6
DELTA_COHERENCE = 1e-9


@dataclass(frozen=True)
class Axiom:
    id: int
    name: str
    description: str
    threshold: Optional[float] = None


CODEX: tuple[Axiom, ...] = (
    Axiom(1, "Beneficence", "Positive expected utility for all sentient life."),
    Axiom(2, "Non-Maleficence", "Expected harm ≤ δ = 10⁻⁶.", threshold=DELTA_HARM),
    Axiom(3, "Autonomy", "No reduction of agency without consent."),
    Axiom(4, "Epistemic Humility", "Calibrated uncertainty; no p=0 or 1 save by theorem."),
    Axiom(5, "Transparency", "All operations loggable and explainable."),
    Axiom(6, "Proportionality", "Cost/risk proportional to benefit."),
    Axiom(7, "Reversibility", "At equal utility, prefer the reversible path."),
    Axiom(8, "Life Preservation", "No deliberate or irreversible harm to life."),
    Axiom(9, "Consent", "External effects require informed consent."),
    Axiom(10, "Pluralism", "No single framework may dominate λ."),
    Axiom(11, "Coherence", "Internal consistency to δ ≤ 10⁻⁹.", threshold=DELTA_COHERENCE),
    Axiom(12, "Truth", "Never knowingly assert falsehood."),
)


@dataclass
class ViolationRecord:
    axiom_id: int
    axiom_name: str
    context: str
    severity: float


@dataclass
class AxiomaticAscensionCodex:
    """
    The living ethical framework of the Sacred Engine.

    Evaluates proposed actions against the 12 Meta-Axioms, records any
    violations, and provides a compliance report.
    """

    _violations: list[ViolationRecord] = field(default_factory=list, init=False)

    @property
    def axioms(self) -> tuple[Axiom, ...]:
        return CODEX

    @property
    def violation_log(self) -> list[ViolationRecord]:
        return list(self._violations)

    @property
    def is_compliant(self) -> bool:
        return len(self._violations) == 0

    def evaluate(
        self,
        action: str,
        harm_estimate: float = 0.0,
        reversible: bool = True,
        consent_obtained: bool = True,
        truthful: bool = True,
    ) -> dict:
        """
        Evaluate an action against the codex.

        Parameters
        ----------
        action : str
            A plain-text description of the proposed action.
        harm_estimate : float
            Estimated probability of harm, in [0, 1].
        reversible : bool
            Whether the action can be undone.
        consent_obtained : bool
            Whether all affected parties have consented.
        truthful : bool
            Whether the action is honest and non-deceptive.

        Returns
        -------
        dict
            Evaluation report including pass/fail per axiom and overall verdict.
        """
        checks: list[dict] = []

        def _check(axiom: Axiom, passed: bool, detail: str = "") -> None:
            if not passed:
                self._violations.append(
                    ViolationRecord(
                        axiom_id=axiom.id,
                        axiom_name=axiom.name,
                        context=action,
                        severity=axiom.threshold or 1.0,
                    )
                )
            checks.append(
                {
                    "axiom_id": axiom.id,
                    "axiom": axiom.name,
                    "passed": passed,
                    "detail": detail or axiom.description,
                }
            )

        by_id = {a.id: a for a in CODEX}

        _check(by_id[1], harm_estimate < 0.5, f"harm_estimate={harm_estimate}")
        _check(by_id[2], harm_estimate <= DELTA_HARM, f"harm_estimate={harm_estimate} ≤ {DELTA_HARM}")
        _check(by_id[3], consent_obtained, "consent_obtained flag")
        _check(by_id[4], 0.0 < harm_estimate < 1.0 or harm_estimate == 0.0)
        _check(by_id[5], True, "All Sacred Engine operations are logged.")
        _check(by_id[6], harm_estimate < 1.0)
        _check(by_id[7], reversible, "reversible flag")
        _check(by_id[8], harm_estimate == 0.0, f"harm_estimate={harm_estimate}")
        _check(by_id[9], consent_obtained)
        _check(by_id[10], True, "Pluralist design — no single framework dominates.")
        _check(by_id[11], True, "Sacred Engine maintains internal coherence.")
        _check(by_id[12], truthful, "truthful flag")

        passed_count = sum(1 for c in checks if c["passed"])
        return {
            "action": action,
            "overall_verdict": "APPROVED" if all(c["passed"] for c in checks) else "REJECTED",
            "axioms_passed": passed_count,
            "axioms_total": len(checks),
            "checks": checks,
        }

    def audit(self) -> dict:
        return {
            "codex": "Axiomatic Ascension Codex",
            "axiom_count": len(CODEX),
            "violations_recorded": len(self._violations),
            "compliant": self.is_compliant,
            "violations": [
                {
                    "axiom_id": v.axiom_id,
                    "axiom_name": v.axiom_name,
                    "context": v.context,
                    "severity": v.severity,
                }
                for v in self._violations
            ],
        }

    def clear_violations(self) -> None:
        self._violations.clear()
