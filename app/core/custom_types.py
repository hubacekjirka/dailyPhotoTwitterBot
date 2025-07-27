from typing import NamedTuple


class Label(NamedTuple):
    name: str
    confidence: int


class GeoCoordinates(NamedTuple):
    latitude: float
    longitude: float
