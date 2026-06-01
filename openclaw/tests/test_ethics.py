import pytest
from openclaw.ethics import AxiomaticAscensionCodex, CODEX, DELTA_HARM


class TestAxiomaticAscensionCodex:
    def test_codex_has_12_axioms(self):
        assert len(CODEX) == 12

    def test_fully_ethical_action_approved(self):
        codex = AxiomaticAscensionCodex()
        report = codex.evaluate(
            "Build a healing temple",
            harm_estimate=0.0,
            reversible=True,
            consent_obtained=True,
            truthful=True,
        )
        assert report["overall_verdict"] == "APPROVED"

    def test_harmful_action_rejected(self):
        codex = AxiomaticAscensionCodex()
        report = codex.evaluate(
            "Detonate structure",
            harm_estimate=0.9,
            reversible=False,
            consent_obtained=False,
            truthful=True,
        )
        assert report["overall_verdict"] == "REJECTED"

    def test_violations_recorded(self):
        codex = AxiomaticAscensionCodex()
        codex.evaluate(
            "Harmful action",
            harm_estimate=1.0,
            reversible=False,
            consent_obtained=False,
            truthful=False,
        )
        assert len(codex.violation_log) > 0

    def test_clear_violations(self):
        codex = AxiomaticAscensionCodex()
        codex.evaluate("Bad thing", harm_estimate=1.0)
        codex.clear_violations()
        assert codex.is_compliant is True

    def test_audit_returns_compliant_initially(self):
        codex = AxiomaticAscensionCodex()
        audit = codex.audit()
        assert audit["compliant"] is True
        assert audit["violations_recorded"] == 0

    def test_harm_at_threshold_passes_non_maleficence(self):
        codex = AxiomaticAscensionCodex()
        report = codex.evaluate(
            "Borderline action",
            harm_estimate=DELTA_HARM,
            reversible=True,
            consent_obtained=True,
            truthful=True,
        )
        non_mal = next(c for c in report["checks"] if c["axiom_id"] == 2)
        assert non_mal["passed"] is True
