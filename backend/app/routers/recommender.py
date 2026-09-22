from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import GymRecommendRequest, GymOut
from app.utils.security import get_current_user
from app.services.recommender_service import recommend_gyms
from app.services.geocode_service import geocode_place

router = APIRouter(prefix="/gyms", tags=["Module 7: Gym Recommender & Planner"])


@router.get("/geocode")
async def geocode(query: str, user: dict = Depends(get_current_user)):
    """Resolves a place name typed by the user into coordinates, so the
    frontend never has to ask for raw latitude/longitude."""
    try:
        result = await geocode_place(query)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"The location lookup service returned an error ({e.response.status_code}). Please try again shortly.",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Couldn't reach the location lookup service - check your internet connection and try again.",
        )

    if not result:
        raise HTTPException(status_code=404, detail=f"Couldn't find a location matching '{query}'")
    return result


@router.post("/recommend", response_model=List[GymOut])
async def get_recommendations(req: GymRecommendRequest, user: dict = Depends(get_current_user)):
    # To go live later: replace recommend_gyms' seeded dataset with a real
    # source (Google Places API "gym" search near lat/lng, or a scraped/
    # partner dataset) - the haversine + goal-scoring logic here stays the same.
    return await recommend_gyms(req.latitude, req.longitude, req.goal, req.max_distance_km)
