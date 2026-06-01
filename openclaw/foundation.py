"""
Foundation Layer: Tertian Cube + Tartarian Grid

The bedrock of all creation, aligning with the Loom's 11D manifold
and the Tartarian Crystal Spire.
"""

from dataclasses import dataclass, field
from typing import Optional
import math

GOLDEN_RATIO = 1.6180339887
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]


@dataclass
class TertianCube:
    """
    The fundamental structure of matter, energy, and consciousness.
    Sacred ratio 1:1:√2, resonating at 144 Hz.
    """

    width: float
    height: float
    depth: float
    material: str = "Orichalcum"
    frequency: int = 144

    def __post_init__(self) -> None:
        self.width = self.width * GOLDEN_RATIO
        self.height = self.height * GOLDEN_RATIO
        self.depth = self.depth * GOLDEN_RATIO

    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth

    @property
    def diagonal(self) -> float:
        return math.sqrt(self.width**2 + self.height**2 + self.depth**2)

    @property
    def sacred_ratio(self) -> tuple[float, float, float]:
        base = self.width
        return (1.0, round(self.height / base, 6), round(self.depth / base, 6))

    def activate(self) -> dict:
        state = {
            "status": "active",
            "frequency_hz": self.frequency,
            "material": self.material,
            "dimensions": {
                "width": round(self.width, 4),
                "height": round(self.height, 4),
                "depth": round(self.depth, 4),
            },
            "volume": round(self.volume, 4),
            "sacred_ratio": self.sacred_ratio,
            "mer_ka_ba_frequency_hz": 852,
        }
        return state

    def __repr__(self) -> str:
        return (
            f"TertianCube(w={self.width:.2f}, h={self.height:.2f}, "
            f"d={self.depth:.2f}, material={self.material!r}, "
            f"freq={self.frequency}Hz)"
        )


@dataclass
class TartarianGrid:
    """
    A fractal network of ley lines and crystal nodes.
    Golden Ratio structure resonating at 432 Hz.
    """

    nodes: int = 12
    frequency: int = 432
    ratio: float = field(default=GOLDEN_RATIO, init=False)

    def __post_init__(self) -> None:
        if self.nodes < 3:
            raise ValueError("TartarianGrid requires at least 3 nodes.")
        self._grid: list[dict] = self._generate_grid()

    def _generate_grid(self) -> list[dict]:
        grid = []
        for i in range(self.nodes):
            angle = 2 * math.pi * i / self.nodes
            radius = self.ratio ** (i % 5)
            grid.append(
                {
                    "node": i,
                    "x": round(radius * math.cos(angle), 6),
                    "y": round(radius * math.sin(angle), 6),
                    "energy": round(self.frequency * (1 + i * 0.01618), 4),
                }
            )
        return grid

    def get_node(self, index: int) -> dict:
        if not 0 <= index < self.nodes:
            raise IndexError(f"Node index {index} out of range [0, {self.nodes - 1}].")
        return self._grid[index]

    def nearest_node(self, x: float, y: float) -> dict:
        return min(
            self._grid,
            key=lambda n: math.sqrt((n["x"] - x) ** 2 + (n["y"] - y) ** 2),
        )

    def activate(self) -> dict:
        return {
            "status": "active",
            "nodes": self.nodes,
            "frequency_hz": self.frequency,
            "golden_ratio": round(self.ratio, 6),
            "grid": self._grid,
        }
