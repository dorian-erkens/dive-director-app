from __future__ import annotations

import math
import httpx

from app.models.wrecks import Wreck, NearbyWreck

SHOM_WFS_URL = "https://services.data.shom.fr/INSPIRE/wfs"
LAYER = "EPAVES_BDD_WFS:wrecks"


def _parse_wreck(feature: dict) -> Wreck:
    props = feature.get("properties", {})

    wreck_id = feature.get("id", "")
    if not wreck_id:
        wreck_id = props.get("inspireid", "unknown")

    # Use lat/lon from properties (always WGS84), not geometry (may be EPSG:3857)
    lat = props.get("latitude", 0.0)
    lon = props.get("longitude", 0.0)

    return Wreck(
        id=wreck_id,
        name=props.get("nom"),
        latitude=lat,
        longitude=lon,
        depth=props.get("brassiage"),
        depth_precision=props.get("precis_bra"),
        ship_info=props.get("caract_bat"),
        object_condition=props.get("caract_obj"),
        sinking_circumstances=props.get("circ_nauf"),
        object_length=props.get("long_obj"),
        position_precision=props.get("precis_loc"),
        object_type=props.get("type_obj"),
        inspire_id=props.get("inspireid"),
    )


def _distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    d_lat = math.radians(lat2 - lat1)
    mean_lat = math.radians((lat1 + lat2) / 2)
    d_lon = math.radians(lon2 - lon1)
    dx = d_lon * math.cos(mean_lat)
    dy = d_lat
    dist_rad = math.sqrt(dx * dx + dy * dy)
    return dist_rad * 3440.065  # radians to nautical miles


def _bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    mean_lat = math.radians((lat1 + lat2) / 2)
    dx = d_lon * math.cos(mean_lat)
    angle = math.degrees(math.atan2(dx, d_lat))
    return angle % 360


async def search_by_name(name: str, max_results: int = 50) -> list[Wreck]:
    safe_name = name.replace("'", "''").replace("%", "").replace("_", "\\_")
    cql_filter = f"nom ILIKE '%{safe_name}%'"

    params = {
        "service": "WFS",
        "version": "1.1.0",
        "request": "GetFeature",
        "typeName": LAYER,
        "outputFormat": "application/json",
        "CQL_FILTER": cql_filter,
        "maxFeatures": str(max_results),
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(SHOM_WFS_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    features = data.get("features", [])
    return [_parse_wreck(f) for f in features]


async def search_bbox(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
    max_results: int = 200,
) -> list[Wreck]:
    # Use CQL property filter on lat/lon (geometry is EPSG:3857, properties are WGS84)
    cql = (
        f"latitude BETWEEN {min_lat} AND {max_lat} "
        f"AND longitude BETWEEN {min_lon} AND {max_lon}"
    )

    params = {
        "service": "WFS",
        "version": "1.1.0",
        "request": "GetFeature",
        "typeName": LAYER,
        "outputFormat": "application/json",
        "CQL_FILTER": cql,
        "maxFeatures": str(max_results),
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(SHOM_WFS_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    return [_parse_wreck(f) for f in data.get("features", [])]


async def get_nearby(
    latitude: float,
    longitude: float,
    radius_nm: float,
    max_results: int = 50,
) -> list[NearbyWreck]:
    deg_margin = radius_nm / 60 * 1.5
    bbox_wrecks = await search_bbox(
        min_lat=latitude - deg_margin,
        max_lat=latitude + deg_margin,
        min_lon=longitude - deg_margin / math.cos(math.radians(latitude)),
        max_lon=longitude + deg_margin / math.cos(math.radians(latitude)),
        max_results=500,
    )

    nearby = []
    for w in bbox_wrecks:
        dist = _distance_nm(latitude, longitude, w.latitude, w.longitude)
        if dist <= radius_nm:
            brg = _bearing(latitude, longitude, w.latitude, w.longitude)
            nearby.append(
                NearbyWreck(
                    **w.model_dump(),
                    distance_nm=round(dist, 2),
                    bearing=round(brg, 1),
                )
            )

    nearby.sort(key=lambda w: w.distance_nm)
    return nearby[:max_results]


async def get_details(wreck_id: str) -> Wreck | None:
    if not wreck_id.startswith("wrecks."):
        wreck_id = f"wrecks.{wreck_id}"

    params = {
        "service": "WFS",
        "version": "1.1.0",
        "request": "GetFeature",
        "typeName": LAYER,
        "outputFormat": "application/json",
        "FEATUREID": wreck_id,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(SHOM_WFS_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    features = data.get("features", [])
    if not features:
        return None
    return _parse_wreck(features[0])
