"""Data models for tour points."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Coordinates:
    """Geographic coordinates."""
    lat: float
    lng: float

    def __str__(self) -> str:
        return f"({self.lat}, {self.lng})"


@dataclass
class Point:
    """Represents a point of interest on a tour route."""
    run_id: str
    point_id: str
    location_name: str
    coordinates: Coordinates
    order: int
    place_id: Optional[str] = None  # Google Maps Place ID
    address: Optional[str] = None

    def __str__(self) -> str:
        return f"Point(#{self.order}: {self.location_name} at {self.coordinates})"
