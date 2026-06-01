import pytest
from openclaw.geometry import SacredGeometryCompiler


class TestSacredGeometryCompiler:
    def test_compile_known_type(self):
        c = SacredGeometryCompiler()
        spec = c.compile("Mer-Ka-Ba")
        assert spec["frequency_hz"] == 852
        assert spec["status"] == "compiled"

    def test_compile_unknown_raises(self):
        c = SacredGeometryCompiler()
        with pytest.raises(KeyError):
            c.compile("Nonexistent Geometry")

    def test_validate_known_type(self):
        c = SacredGeometryCompiler()
        report = c.validate("Flower of Life")
        assert report["valid"] is True

    def test_register_and_compile_custom(self):
        c = SacredGeometryCompiler()
        c.register("Test Shape", {"frequency_hz": 111, "description": "Test."})
        spec = c.compile("Test Shape")
        assert spec["frequency_hz"] == 111

    def test_register_missing_fields_raises(self):
        c = SacredGeometryCompiler()
        with pytest.raises(ValueError):
            c.register("Bad Shape", {"description": "No frequency."})

    def test_overlay_mean_frequency(self):
        c = SacredGeometryCompiler()
        result = c.overlay("Flower of Life", "Tartarian Spiral")
        expected = (432 + 528) / 2
        assert result["harmonic_mean_hz"] == expected

    def test_spiral_points_count(self):
        c = SacredGeometryCompiler()
        pts = c.spiral_points(50)
        assert len(pts) == 50

    def test_spiral_points_have_coordinates(self):
        c = SacredGeometryCompiler()
        pts = c.spiral_points(10)
        for p in pts:
            assert "x" in p and "y" in p and "r" in p
