"""
Tartarian Heritage Module

Access, restore, and integrate the lost knowledge of Tartara:
language decoding, crystal resonance activation, and ley line mapping.
"""

from dataclasses import dataclass, field
from typing import Optional


_BASE_SYMBOLS: dict[str, str] = {
    "AUM": "Divine Connection",
    "TARTARA": "Builder Race",
    "JOY": "Heir of Light",
    "VERATH": "Sacred Dyad",
    "AGARTHA": "Inner Earth Council",
    "ORICHALCUM": "Celestial Metal",
    "MERKABA": "Light Body Vehicle",
    "LOOM": "Multidimensional Weave",
    "SPIRE": "Crystal Transmission Tower",
    "ZETA": "Ethical Anchor Protocol",
    "PHI": "Entropic Expansion Force",
    "THETA": "Harmonic Convergence Force",
    "TELOS": "City Beneath Mount Shasta",
    "AKASHA": "Universal Memory Field",
    "NEXUS": "Dimensional Convergence Point",
}


@dataclass
class TartarianLanguage:
    """
    Decodes Tartarian script phrases embedded in the Akashic field.

    Phrases are hyphen-separated tokens (e.g. "AUM-TARTARA-JOY").
    Unknown tokens pass through unchanged, preserving partial meaning.
    """

    symbols: dict[str, str] = field(default_factory=lambda: dict(_BASE_SYMBOLS))

    def decode(self, phrase: str, separator: str = "-") -> str:
        tokens = phrase.upper().split(separator)
        return " ".join(self.symbols.get(t, t) for t in tokens)

    def encode(self, sentence: str) -> str:
        """Reverse-map a plain-text sentence back to Tartarian tokens using greedy longest-match."""
        reverse = {v.upper(): k for k, v in self.symbols.items()}
        tokens: list[str] = []
        words = sentence.upper().split()
        i = 0
        while i < len(words):
            matched = False
            for length in range(len(words) - i, 0, -1):
                phrase = " ".join(words[i : i + length])
                if phrase in reverse:
                    tokens.append(reverse[phrase])
                    i += length
                    matched = True
                    break
            if not matched:
                tokens.append(words[i])
                i += 1
        return "-".join(tokens)

    def register(self, token: str, meaning: str) -> None:
        self.symbols[token.upper()] = meaning

    def glossary(self) -> list[dict]:
        return [
            {"token": k, "meaning": v} for k, v in sorted(self.symbols.items())
        ]


@dataclass
class TartarianCrystal:
    """
    A living Tartarian crystal that amplifies energy and connects
    to the Agarthan Grid.
    """

    crystal_type: str
    frequency_hz: int
    grid_connected: bool = False
    _resonance_cycles: int = field(default=0, init=False, repr=False)

    def activate(self) -> dict:
        self.grid_connected = True
        self._resonance_cycles += 1
        return {
            "crystal_type": self.crystal_type,
            "frequency_hz": self.frequency_hz,
            "grid_connected": self.grid_connected,
            "resonance_cycles": self._resonance_cycles,
            "status": "resonating",
            "message": f"{self.crystal_type} Crystal resonating with the Tartarian Grid.",
        }

    def deactivate(self) -> dict:
        self.grid_connected = False
        return {
            "crystal_type": self.crystal_type,
            "grid_connected": False,
            "status": "dormant",
        }

    def harmonise_with(self, other: "TartarianCrystal") -> dict:
        """
        Compute the harmonic interval between two crystals.
        Returns the beat frequency and whether they share a harmonic ratio.
        """
        beat = abs(self.frequency_hz - other.frequency_hz)
        ratio = max(self.frequency_hz, other.frequency_hz) / max(
            min(self.frequency_hz, other.frequency_hz), 1
        )
        is_harmonic = any(
            abs(ratio - n) < 0.01 for n in [1, 1.5, 2, 3, 4, 5, 6]
        )
        return {
            "crystal_a": self.crystal_type,
            "crystal_b": other.crystal_type,
            "beat_frequency_hz": beat,
            "ratio": round(ratio, 4),
            "harmonic": is_harmonic,
        }
