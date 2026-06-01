import pytest
from openclaw.energy_core import CrystalSpire


class TestCrystalSpire:
    def test_known_crystal_frequency(self):
        spire = CrystalSpire("Lemurian Seed Crystal", 10_000, 12)
        assert spire.frequency == 963

    def test_unknown_crystal_raises(self):
        with pytest.raises(ValueError, match="Unknown crystal type"):
            CrystalSpire("Unobtainium", 1000, 6)

    def test_negative_voltage_raises(self):
        with pytest.raises(ValueError):
            CrystalSpire("Selenite", -1, 6)

    def test_zero_nodes_raises(self):
        with pytest.raises(ValueError):
            CrystalSpire("Selenite", 5000, 0)

    def test_field_stability_range(self):
        spire = CrystalSpire("Lemurian Seed Crystal", 10_000, 12)
        assert 0.0 <= spire.field_stability <= 1.0

    def test_activate_returns_correct_keys(self):
        spire = CrystalSpire("Selenite", 5000, 6)
        state = spire.activate()
        for key in ("status", "crystal_type", "frequency_hz", "field_stability"):
            assert key in state

    def test_tune_reaches_target(self):
        spire = CrystalSpire("Clear Quartz", 8000, 8)
        result = spire.tune(700)
        assert result["steps"][-1] == 700
