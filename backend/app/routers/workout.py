from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends

from app.models.schemas import WorkoutSessionIn, WorkoutSessionOut
from app.database import get_supabase
from app.utils.security import get_current_user
from app.services.workout_service import analyze_session

router = APIRouter(prefix="/workout", tags=["Module 1: AI Gym Trainer"])


def _serialize_reps(reps):
    # Pydantic RepEvent objects -> plain JSON-safe dicts for the jsonb column
    return [
        {
            "exercise": r.exercise,
            "joint_angle": r.joint_angle,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in reps
    ]


@router.post("/session", response_model=WorkoutSessionOut)
async def log_session(session: WorkoutSessionIn, user: dict = Depends(get_current_user)):
    """
    Ingest a completed set from the frontend (rep angles come from MediaPipe
    Pose, client-side in React or server-side in Streamlit). Returns rep
    count + real-time form feedback.
    """
    analysis = analyze_session(session.exercise, session.reps, session.duration_seconds, session.form_issues)

    doc = {
        "user_id": user["id"],
        "exercise": session.exercise,
        "reps": _serialize_reps(session.reps),
        "duration_seconds": session.duration_seconds,
        "form_issues": session.form_issues,
        "rep_count": analysis["rep_count"],
        "feedback": analysis["feedback"],
        "form_score": analysis["form_score"],
        "tempo_consistency": analysis["tempo_consistency"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    supabase = get_supabase()
    result = await supabase.table("workout_sessions").insert(doc).execute()
    return result.data[0]


@router.get("/history", response_model=List[WorkoutSessionOut])
async def get_history(user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    result = (
        await supabase.table("workout_sessions")
        .select("*")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    return result.data
