from fastapi import APIRouter, Query

from app.models.wrecks import NearbyWreckResult, Wreck, WreckSearchResult
from app.services import shom

router = APIRouter(prefix="/api/wrecks", tags=["wrecks"])


@router.get("/search", response_model=WreckSearchResult)
async def search_wrecks(name: str = Query(..., min_length=1)):
    wrecks = await shom.search_by_name(name)
    return WreckSearchResult(wrecks=wrecks, total=len(wrecks))


@router.get("/nearby", response_model=NearbyWreckResult)
async def nearby_wrecks(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius: float = Query(5.0, gt=0, le=50),
    limit: int = Query(50, gt=0, le=500),
):
    wrecks = await shom.get_nearby(lat, lon, radius, limit)
    return NearbyWreckResult(
        wrecks=wrecks,
        total=len(wrecks),
        center_lat=lat,
        center_lon=lon,
        radius_nm=radius,
    )


@router.get("/bbox", response_model=WreckSearchResult)
async def bbox_wrecks(
    min_lat: float = Query(...),
    max_lat: float = Query(...),
    min_lon: float = Query(...),
    max_lon: float = Query(...),
    limit: int = Query(200, gt=0, le=1000),
):
    wrecks = await shom.search_bbox(min_lat, max_lat, min_lon, max_lon, limit)
    return WreckSearchResult(wrecks=wrecks, total=len(wrecks))


@router.get("/{wreck_id}", response_model=Wreck)
async def wreck_details(wreck_id: str):
    wreck = await shom.get_details(wreck_id)
    if not wreck:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Épave non trouvée")
    return wreck
