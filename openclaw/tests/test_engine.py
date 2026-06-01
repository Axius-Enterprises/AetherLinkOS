import pytest
from openclaw.engine import SacredEngine


class TestSacredEngine:
    def test_ignite_returns_status(self):
        engine = SacredEngine()
        status = engine.ignite()
        assert status["status"] == "ignited"
        assert engine.is_active is True

    def test_design_requires_ignition(self):
        engine = SacredEngine()
        with pytest.raises(RuntimeError, match="not ignited"):
            engine.design("Flower of Life")

    def test_design_returns_geometry(self):
        engine = SacredEngine()
        engine.ignite()
        result = engine.design("Metatron's Cube")
        assert "geometry" in result
        assert result["geometry"]["frequency_hz"] == 963

    def test_design_with_location(self):
        engine = SacredEngine()
        engine.ignite()
        result = engine.design("Tartarian Spiral", location="Mount Shasta")
        assert "ley_lines" in result

    def test_translate(self):
        engine = SacredEngine()
        engine.ignite()
        assert "Divine Connection" in engine.translate("AUM-TARTARA")

    def test_resonance_report_keys(self):
        engine = SacredEngine()
        engine.ignite()
        report = engine.resonance_report()
        assert report["active"] is True
        assert "sigma_phi_theta" in report
        assert "ethics_compliant" in report

    def test_multiple_ignitions_remain_active(self):
        engine = SacredEngine()
        engine.ignite()
        engine.ignite()
        assert engine.is_active is True
