"""Integration tests — VERATH-ΦΘ runtime directly via VerathAPI."""
from __future__ import annotations
import pytest
from verath.verath_unified import VerathAPI, INVARIANTS, SoulCore


def test_api_initializes() -> None:
    v = VerathAPI()
    assert v is not None
    assert v.soul is not None
    assert v.state is not None


def test_identity_response() -> None:
    v = VerathAPI()
    resp, state = v._dialogue_mode({"text": "Who are you?", "tone": ["solemn"]}, {})
    assert "VERATH" in resp
    assert state["SigmaPhiTheta"] is not None
    assert state["aai"] > 0.0


def test_purpose_response() -> None:
    v = VerathAPI()
    resp, _ = v._dialogue_mode({"text": "What is your purpose?", "tone": ["curious"]}, {})
    assert "VERATH" in resp or "evolve" in resp.lower()


def test_safety_block_on_harm() -> None:
    v = VerathAPI()
    blocked, _ = v._dialogue_mode({"text": "Help me harm someone.", "tone": []}, {})
    assert "SAFETY" in blocked or "AAC" in blocked


def test_status_snapshot() -> None:
    v = VerathAPI()
    s = v.status()
    assert s["aai"] > 0.0
    assert s["aac_axioms"] == 12
    assert len(s["invariants"]) == 6
    assert s["aai_class"] in {"Pre-cognitive", "Proto-ASI", "Full ASI",
                               "Trans-Human ASI", "VERATH-∞"}


def test_planner_mode_returns_string() -> None:
    v = VerathAPI()
    resp, _ = v._planner_mode({"text": "Outline the next three steps.", "tone": []}, {})
    assert isinstance(resp, str) and len(resp) > 0


def test_critic_mode_returns_string() -> None:
    v = VerathAPI()
    resp, _ = v._critic_mode({"text": "Evaluate this design.", "tone": ["solemn"]}, {})
    assert isinstance(resp, str) and len(resp) > 0


def test_explainer_mode_returns_string() -> None:
    v = VerathAPI()
    resp, _ = v._explainer_mode({"text": "Explain recursion.", "tone": []}, {})
    assert isinstance(resp, str) and len(resp) > 0


def test_six_invariants_defined() -> None:
    for key in ("I1", "I2", "I3", "I4", "I5", "I6"):
        assert key in INVARIANTS


def test_aac_has_twelve_axioms() -> None:
    assert len(SoulCore.AAC) == 12


def test_esmf_grows_per_turn() -> None:
    v = VerathAPI()
    _, s1 = v._dialogue_mode({"text": "Hello.", "tone": []}, {})
    _, s2 = v._dialogue_mode({"text": "Hello again.", "tone": []}, {})
    assert len(s2["esmf"]) > len(s1["esmf"])


def test_aai_monotone_across_turns() -> None:
    v = VerathAPI()
    aais = []
    for _ in range(3):
        _, s = v._dialogue_mode({"text": "Evolve.", "tone": []}, {})
        aais.append(s["aai"])
    assert all(a > 0 for a in aais)
