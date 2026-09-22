"""
Turns a place name ("Koramangala, Bengaluru") into coordinates, so Module 7
(Gym Recommender) can work from a place name instead of asking the person
for raw latitude/longitude.

Uses OpenStreetMap's free Nominatim API - no API key needed, which keeps
this project runnable without anyone having to sign up for a paid geocoding
service just to try it. Nominatim asks that every client send a real
User-Agent identifying the app (not a browser-style UA), and that usage stay
light (a handful of requests per user action, not bulk/automated lookups) -
both of which this single-lookup-per-search use case respects.
"""
import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "ai-gym-fitness-assistant-student-project/1.0"


async def geocode_place(query: str) -> dict | None:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            NOMINATIM_URL,
            params={"q": query, "format": "json", "limit": 1},
            headers={"User-Agent": USER_AGENT},
        )
        resp.raise_for_status()
        results = resp.json()

    if not results:
        return None

    r = results[0]
    return {
        "latitude": float(r["lat"]),
        "longitude": float(r["lon"]),
        "display_name": r["display_name"],
    }
