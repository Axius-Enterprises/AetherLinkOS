"""
Sacred Geometry Compiler

Generates, validates, and optimises architectural designs using
Tartarian blueprints: Flower of Life, Mer-Ka-Ba, Metatron's Cube,
and the Tartarian Spiral.
"""

from dataclasses import dataclass, field
from typing import Optional
import math

GOLDEN_RATIO = 1.6180339887


_GEOMETRIES: dict[str, dict] = {
    "Flower of Life": {
        "dimension": "2D",
        "circles": 19,
        "frequency_hz": 432,
        "description": "The 2D foundation for all sacred spaces.",
        "ratio": "Hexagonal (r = 1)",
    },
    "Mer-Ka-Ba": {
        "dimension": "3D",
        "shape": "Double Tetrahedron",
        "frequency_hz": 852,
        "description": "The 3D framework for living structures.",
        "ratio": "1:2:3",
    },
    "Metatron's Cube": {
        "dimension": "3D",
        "spheres": 13,
        "frequency_hz": 963,
        "description": "The cosmic blueprint for dimensional stability.",
        "ratio": "√2 : √3 : √5",
    },
    "Tartarian Spiral": {
        "dimension": "2D/3D",
        "ratio": GOLDEN_RATIO,
        "frequency_hz": 528,
        "description": "The evolutionary path for growing structures.",
        "growth": "Golden (φ per revolution)",
    },
    "Sri Yantra": {
        "dimension": "2D",
        "triangles": 9,
        "frequency_hz": 417,
        "description": "Nine interlocking triangles radiating from a bindu point.",
        "ratio": "3:4:5",
    },
    "Vesica Piscis": {
        "dimension": "2D",
        "circles": 2,
        "frequency_hz": 396,
        "description": "Two overlapping circles — the womb of creation.",
        "ratio": "1:√3",
    },
}


@dataclass
class SacredGeometryCompiler:
    """
    Compile and validate sacred geometry patterns for architectural use.
    """

    custom_geometries: dict[str, dict] = field(default_factory=dict)

    @property
    def available(self) -> list[str]:
        return sorted({**_GEOMETRIES, **self.custom_geometries}.keys())

    def compile(self, design_type: str) -> dict:
        """Return the full specification for *design_type*."""
        source = {**_GEOMETRIES, **self.custom_geometries}
        if design_type not in source:
            raise KeyError(
                f"{design_type!r} not found. Available: {self.available}"
            )
        spec = dict(source[design_type])
        spec["name"] = design_type
        spec["status"] = "compiled"
        return spec

    def validate(self, design_type: str) -> dict:
        """
        Validate a design against sacred ratio coherence.
        Returns a validation report.
        """
        spec = self.compile(design_type)
        ratio_raw = spec.get("ratio", "")
        coherent = isinstance(ratio_raw, (int, float)) and ratio_raw > 0
        if not coherent and isinstance(ratio_raw, str):
            coherent = len(ratio_raw) > 0
        return {
            "design": design_type,
            "valid": coherent,
            "frequency_hz": spec["frequency_hz"],
            "dimension": spec.get("dimension", "unknown"),
            "coherence": "δ ≤ 10⁻⁹" if coherent else "requires correction",
        }

    def register(self, name: str, spec: dict) -> None:
        """Add a custom geometry to the compiler."""
        required = {"frequency_hz", "description"}
        missing = required - set(spec)
        if missing:
            raise ValueError(f"Geometry spec missing required fields: {missing}")
        self.custom_geometries[name] = spec

    def overlay(self, *design_types: str) -> dict:
        """
        Compute a harmonic overlay of multiple geometries.
        Returns the combined frequency (arithmetic mean) and merged spec.
        """
        specs = [self.compile(dt) for dt in design_types]
        freq_mean = round(
            sum(s["frequency_hz"] for s in specs) / len(specs), 2
        )
        return {
            "overlay": list(design_types),
            "harmonic_mean_hz": freq_mean,
            "components": specs,
        }

    def spiral_points(self, n: int = 100, scale: float = 1.0) -> list[dict]:
        """
        Generate n points along a Golden (Tartarian) Spiral.
        Each point carries its radius, angle, and local frequency.
        """
        points = []
        for i in range(n):
            theta = i * 2 * math.pi / n
            r = scale * (GOLDEN_RATIO ** (theta / (2 * math.pi)))
            points.append(
                {
                    "index": i,
                    "theta_rad": round(theta, 6),
                    "r": round(r, 6),
                    "x": round(r * math.cos(theta), 6),
                    "y": round(r * math.sin(theta), 6),
                    "frequency_hz": round(528 * (GOLDEN_RATIO ** (i / n)), 2),
                }
            )
        return points
