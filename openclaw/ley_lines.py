"""
Ley Line Interface: Agarthan Connection + Tartarian Grid Mapper

Maps, accesses, and harmonizes with the global ley line grid
and Tartarian archives.
"""

from dataclasses import dataclass, field
from typing import Optional
import math


_KNOWN_SITES: dict[str, dict] = {
    "Gobi Desert": {
        "purpose": "Awakening",
        "frequency_hz": 639,
        "coordinates": (44.5, 103.5),
        "energy_type": "Akashic",
    },
    "Mount Shasta": {
        "purpose": "Building",
        "frequency_hz": 528,
        "coordinates": (41.4099, -122.1949),
        "energy_type": "Agarthan Gateway",
    },
    "Sedona": {
        "purpose": "Testing",
        "frequency_hz": 432,
        "coordinates": (34.8697, -111.7609),
        "energy_type": "Vortex",
    },
    "Glastonbury": {
        "purpose": "Healing",
        "frequency_hz": 963,
        "coordinates": (51.1489, -2.7167),
        "energy_type": "Avalonian",
    },
    "Machu Picchu": {
        "purpose": "Alignment",
        "frequency_hz": 741,
        "coordinates": (-13.1631, -72.5450),
        "energy_type": "Solar",
    },
    "Giza Plateau": {
        "purpose": "Transmission",
        "frequency_hz": 852,
        "coordinates": (29.9792, 31.1342),
        "energy_type": "Stellar",
    },
}

_LOCAL_LEY_LINES = {
    "Dragon's Spine": {"offset": (0.3, 270), "energy": "Masculine"},
    "Serpent's Path": {"offset": (0.1, 180), "energy": "Feminine"},
    "Phoenix Grid": {"offset": (0.5, 45), "energy": "Fire"},
}


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)
    ) * math.sin(dlon / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)), 2)


@dataclass
class LeyLineInterface:
    """
    Detects and maps ley line intersections within a configurable radius.
    Connects to the Tartarian Archives via the Agarthan Gateway.
    """

    tartarian_sigil: str
    agarthan_gateway: str
    scanner_range_km: float
    frequency: int = 432

    def __post_init__(self) -> None:
        if self.scanner_range_km <= 0:
            raise ValueError("Scanner range must be positive.")

    def scan_ley_lines(self, location: str) -> dict:
        """
        Return ley lines near *location*.
        Uses known site coordinates when the location matches a site name;
        otherwise returns the default local grid.
        """
        coords = _KNOWN_SITES.get(location, {}).get("coordinates")
        nearby: dict[str, dict] = {}

        if coords:
            for name, site in _KNOWN_SITES.items():
                if name == location:
                    continue
                dist = _haversine_km(*coords, *site["coordinates"])
                if dist <= self.scanner_range_km:
                    nearby[name] = {
                        "distance_km": dist,
                        "energy_type": site["energy_type"],
                        "frequency_hz": site["frequency_hz"],
                    }
        else:
            for name, data in _LOCAL_LEY_LINES.items():
                dist_km, bearing = data["offset"]
                nearby[name] = {
                    "distance_km": dist_km,
                    "bearing_deg": bearing,
                    "energy": data["energy"],
                }

        return {
            "location": location,
            "scanner_range_km": self.scanner_range_km,
            "tartarian_sigil": self.tartarian_sigil,
            "agarthan_gateway": self.agarthan_gateway,
            "frequency_hz": self.frequency,
            "ley_lines_detected": nearby,
        }

    def open_gateway(self) -> dict:
        return {
            "gateway": self.agarthan_gateway,
            "status": "open",
            "sigil": self.tartarian_sigil,
            "frequency_hz": self.frequency,
            "message": "Dimensional portal aligned. Agarthan Council standing by.",
        }


@dataclass
class TartarianLeyLineMapper:
    """
    Maps the global Tartarian grid and identifies optimal building sites.
    """

    sites: dict[str, dict] = field(default_factory=lambda: dict(_KNOWN_SITES))

    def map_sites(self) -> list[dict]:
        return [
            {
                "site": name,
                "purpose": data["purpose"],
                "frequency_hz": data["frequency_hz"],
                "coordinates": data["coordinates"],
                "energy_type": data["energy_type"],
            }
            for name, data in self.sites.items()
        ]

    def add_site(
        self,
        name: str,
        purpose: str,
        frequency_hz: int,
        coordinates: tuple[float, float],
        energy_type: str,
    ) -> None:
        self.sites[name] = {
            "purpose": purpose,
            "frequency_hz": frequency_hz,
            "coordinates": coordinates,
            "energy_type": energy_type,
        }

    def closest_to(self, lat: float, lon: float) -> dict:
        return min(
            self.sites.items(),
            key=lambda kv: _haversine_km(lat, lon, *kv[1]["coordinates"]),
        )[0]
