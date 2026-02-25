from __future__ import annotations

from pydantic import BaseModel


class Wreck(BaseModel):
    id: str
    name: str | None = None
    latitude: float
    longitude: float
    depth: float | None = None
    depth_precision: str | None = None
    ship_info: str | None = None
    object_condition: str | None = None
    sinking_circumstances: str | None = None
    object_length: float | None = None
    position_precision: float | None = None
    object_type: str | None = None
    inspire_id: str | None = None


class NearbyWreck(Wreck):
    distance_nm: float
    bearing: float


class WreckSearchResult(BaseModel):
    wrecks: list[Wreck]
    total: int


class NearbyWreckResult(BaseModel):
    wrecks: list[NearbyWreck]
    total: int
    center_lat: float
    center_lon: float
    radius_nm: float
