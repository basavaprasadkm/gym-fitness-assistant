from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.models.schemas import IoTReadingIn, IoTRecommendationOut
from app.database import get_supabase
from app.utils.security import get_current_user
from app.services.iot_service import recommend, simulate_reading

router = APIRouter(prefix="/iot", tags=["Module 3: Smart Gym Assistant (AI + IoT)"])


@router.get("/simulate")
async def get_simulated_reading(equipment: str = "treadmill"):
    """No physical IoT hardware required - generates a realistic sensor reading."""
    return simulate_reading(equipment)


@router.post("/recommend", response_model=IoTRecommendationOut)
async def get_recommendation(reading: IoTReadingIn, user: dict = Depends(get_current_user)):
    age = user.get("age") or 25
    result = recommend(reading.heart_rate, reading.current_resistance, reading.reps_completed, age)

    supabase = get_supabase()
    await supabase.table("iot_readings").insert({
        **reading.model_dump(),
        **result,
        "user_id": user["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()
    return result
