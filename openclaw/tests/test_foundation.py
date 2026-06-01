import math
import pytest
from openclaw.foundation import TertianCube, TartarianGrid, GOLDEN_RATIO


class TestTertianCube:
    def test_golden_ratio_scaling(self):
        cube = TertianCube(10, 10, 10)
        assert math.isclose(cube.width, 10 * GOLDEN_RATIO)
        assert math.isclose(cube.height, 10 * GOLDEN_RATIO)
        assert math.isclose(cube.depth, 10 * GOLDEN_RATIO)

    def test_volume(self):
        cube = TertianCube(1, 1, 1)
        expected = (GOLDEN_RATIO) ** 3
        assert math.isclose(cube.volume, expected)

    def test_activate_returns_dict(self):
        cube = TertianCube(5, 5, 5)
        state = cube.activate()
        assert state["status"] == "active"
        assert state["frequency_hz"] == 144
        assert state["material"] == "Orichalcum"

    def test_sacred_ratio_is_unity(self):
        cube = TertianCube(4, 4, 4)
        r = cube.sacred_ratio
        assert r[0] == 1.0
        assert math.isclose(r[1], 1.0)
        assert math.isclose(r[2], 1.0)


class TestTartarianGrid:
    def test_node_count(self):
        grid = TartarianGrid(nodes=8)
        assert len(grid.activate()["grid"]) == 8

    def test_minimum_nodes(self):
        with pytest.raises(ValueError):
            TartarianGrid(nodes=2)

    def test_nearest_node_returns_valid(self):
        grid = TartarianGrid(nodes=6)
        node = grid.nearest_node(0.0, 0.0)
        assert "node" in node

    def test_get_node_out_of_range(self):
        grid = TartarianGrid(nodes=5)
        with pytest.raises(IndexError):
            grid.get_node(10)
