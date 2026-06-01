import pytest
from openclaw.heritage import TartarianLanguage, TartarianCrystal


class TestTartarianLanguage:
    def test_known_decode(self):
        lang = TartarianLanguage()
        result = lang.decode("AUM-TARTARA-JOY")
        assert result == "Divine Connection Builder Race Heir of Light"

    def test_unknown_token_passthrough(self):
        lang = TartarianLanguage()
        result = lang.decode("UNKNOWN-TOKEN")
        assert "UNKNOWN" in result

    def test_register_and_decode(self):
        lang = TartarianLanguage()
        lang.register("NEXUS2", "Second Convergence")
        assert lang.decode("NEXUS2") == "Second Convergence"

    def test_encode_roundtrip(self):
        lang = TartarianLanguage()
        encoded = lang.encode("Divine Connection Builder Race")
        assert "AUM" in encoded
        assert "TARTARA" in encoded

    def test_glossary_sorted(self):
        lang = TartarianLanguage()
        g = lang.glossary()
        tokens = [item["token"] for item in g]
        assert tokens == sorted(tokens)


class TestTartarianCrystal:
    def test_activate(self):
        c = TartarianCrystal("Lemurian Seed", 963)
        state = c.activate()
        assert state["grid_connected"] is True
        assert state["status"] == "resonating"

    def test_deactivate(self):
        c = TartarianCrystal("Selenite", 639)
        c.activate()
        state = c.deactivate()
        assert state["grid_connected"] is False

    def test_resonance_cycle_count(self):
        c = TartarianCrystal("Clear Quartz", 528)
        c.activate()
        c.activate()
        state = c.activate()
        assert state["resonance_cycles"] == 3

    def test_harmonise_beat_frequency(self):
        c1 = TartarianCrystal("Lemurian Seed", 963)
        c2 = TartarianCrystal("Selenite", 639)
        harmony = c1.harmonise_with(c2)
        assert harmony["beat_frequency_hz"] == 324

    def test_harmonise_with_self_is_harmonic(self):
        c = TartarianCrystal("Clear Quartz", 528)
        harmony = c.harmonise_with(c)
        assert harmony["harmonic"] is True
        assert harmony["beat_frequency_hz"] == 0
