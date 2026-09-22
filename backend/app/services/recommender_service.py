"""
Module 7: Gym Recommender & Planner.

Uses a small "gym directory" dataset (seeded into the Supabase `gyms` table
on app startup, if empty) and recommends by haversine distance from the
user's coordinates plus a simple goal->program match, mimicking a real
recommendation engine without needing a paid Places API. Swapping GYM_SEED
for a live Google Places / OSM feed later is a drop-in change - the rest of
the pipeline (distance + goal scoring) stays the same.
"""
import math
from app.database import get_supabase

GYM_SEED = [
    {"name": "PowerHouse Fitness", "lat_offset": 0.01, "lng_offset": 0.01,
     "programs": ["strength", "gain"], "rating": 4.5},
    {"name": "CardioZone Gym", "lat_offset": -0.015, "lng_offset": 0.008,
     "programs": ["lose", "cardio"], "rating": 4.2},
    {"name": "FlexFit Studio", "lat_offset": 0.006, "lng_offset": -0.012,
     "programs": ["maintain", "flexibility"], "rating": 4.6},
    {"name": "IronCore Gym", "lat_offset": -0.02, "lng_offset": -0.02,
     "programs": ["strength", "gain"], "rating": 4.0},
    {"name": "LeanLife Fitness Club", "lat_offset": 0.025, "lng_offset": 0.003,
     "programs": ["lose", "maintain"], "rating": 4.3},
    {"name": "PeakForm Athletics", "lat_offset": -0.008, "lng_offset": 0.02,
     "programs": ["strength", "cardio", "gain"], "rating": 4.7},
]


async def ensure_seeded():
    supabase = get_supabase()
    resp = await supabase.table("gyms").select("id").limit(1).execute()
    if not resp.data:
        await supabase.table("gyms").insert(GYM_SEED).execute()


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return round(r * 2 * math.asin(math.sqrt(a)), 2)


async def recommend_gyms(latitude: float, longitude: float, goal: str | None, max_distance_km: float):
    supabase = get_supabase()
    gyms_resp = await supabase.table("gyms").select("*").execute()
    gyms = gyms_resp.data or []

    results = []
    for gym in gyms:
        gym_lat = latitude + gym["lat_offset"]
        gym_lng = longitude + gym["lng_offset"]
        distance = haversine_km(latitude, longitude, gym_lat, gym_lng)
        if distance > max_distance_km:
            continue
        goal_match = (goal in gym["programs"]) if goal else True
        results.append({
            "name": gym["name"],
            "distance_km": distance,
            "programs": gym["programs"],
            "rating": gym["rating"],
            "_goal_match": goal_match,
        })

    # Goal-matching gyms first, then by rating desc, then by distance asc
    results.sort(key=lambda g: (not g["_goal_match"], -g["rating"], g["distance_km"]))
    for r in results:
        r.pop("_goal_match", None)
    return results
