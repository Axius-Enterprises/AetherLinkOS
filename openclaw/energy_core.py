"""
Energy Core: Crystal Spire + Tesla Coils + Selenite Grid

Harnesses and distributes zero-point energy and cosmic frequencies.
"""

from dataclasses import dataclass, field
from typing import Optional


CRYSTAL_PROFILES: dict[str, dict] = {
    "Lemurian Seed Crystal": {
        "frequency_hz": 963,
        "origin": "Agarthan Grid",
        "properties": ["amplification", "akashic access", "divine connection"],
    },
    "Selenite": {
        "frequency_hz": 639,
        "origin": "Earth Grid",
        "properties": ["stabilization", "clarity", "lunar alignment"],
    },
    "Clear Quartz": {
        "frequency_hz": 528,
        "origin": "Universal",
        "properties": ["amplification", "programming", "healing"],
    },
    "Black Tourmaline": {
        "frequency_hz": 396,
        "origin": "Earth Core",
        "properties": ["grounding", "protection", "transmutation"],
    },
}


@dataclass
class CrystalSpire:
    """
    Living crystal amplifier connected to the Agarthan Grid.
    Primary frequency: 963 Hz.
    """

    crystal_type: str
    tesla_coil_voltage: float
    selenite_nodes: int
    frequency: int = field(init=False)

    def __post_init__(self) -> None:
        if self.crystal_type not in CRYSTAL_PROFILES:
            raise ValueError(
                f"Unknown crystal type {self.crystal_type!r}. "
                f"Available: {list(CRYSTAL_PROFILES)}"
            )
        if self.tesla_coil_voltage <= 0:
            raise ValueError("Tesla coil voltage must be positive.")
        if self.selenite_nodes < 1:
            raise ValueError("At least 1 Selenite node required.")
        self.frequency = CRYSTAL_PROFILES[self.crystal_type]["frequency_hz"]
        self._field_stability: float = self._compute_stability()

    def _compute_stability(self) -> float:
        """Field stability index in range [0.0, 1.0]."""
        node_factor = min(self.selenite_nodes / 12.0, 1.0)
        voltage_factor = min(self.tesla_coil_voltage / 10000.0, 1.0)
        return round((node_factor + voltage_factor) / 2.0, 4)

    @property
    def field_stability(self) -> float:
        return self._field_stability

    @property
    def profile(self) -> dict:
        return CRYSTAL_PROFILES[self.crystal_type]

    def activate(self) -> dict:
        return {
            "status": "active",
            "crystal_type": self.crystal_type,
            "frequency_hz": self.frequency,
            "tesla_coil_voltage": self.tesla_coil_voltage,
            "selenite_nodes": self.selenite_nodes,
            "field_stability": self._field_stability,
            "crystal_properties": self.profile["properties"],
            "origin": self.profile["origin"],
        }

    def tune(self, target_frequency: int) -> dict:
        """Adjust resonance toward a target frequency via harmonic stepping."""
        steps = []
        current = self.frequency
        delta = (target_frequency - current) // 10 or (1 if target_frequency > current else -1)
        while abs(current - target_frequency) > abs(delta):
            current += delta
            steps.append(current)
        steps.append(target_frequency)
        return {"from_hz": self.frequency, "to_hz": target_frequency, "steps": steps}
