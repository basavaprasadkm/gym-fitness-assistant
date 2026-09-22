from fastapi import APIRouter, Depends

from app.models.schemas import HabitLogIn, HabitPredictionOut
from app.database import get_supabase
from app.utils.security import get_current_user
from app.services.habit_service import compute_streak, predict_skip_risk, build_nudge

router = APIRouter(prefix="/habit", tags=["Module 4: AI Fitness Habit Tracker"])


@router.post("/log")
async def log_habit(entry: HabitLogIn, user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    doc = {**entry.model_dump(), "user_id": user["id"]}
    # one row per user per day - upsert on the (user_id, date) unique constraint
    await supabase.table("habit_logs").upsert(doc, on_conflict="user_id,date").execute()
    return {"status": "logged"}


@router.get("/prediction", response_model=HabitPredictionOut)
async def get_prediction(user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    resp = (
        await supabase.table("habit_logs")
        .select("*")
        .eq("user_id", user["id"])
        .order("date", desc=True)
        .limit(90)
        .execute()
    )
    logs = resp.data or []
    streak = compute_streak(logs)
    risk = predict_skip_risk(logs)
    nudge = build_nudge(risk, streak)
    return {"skip_risk_percent": risk, "current_streak": streak, "nudge_message": nudge}
