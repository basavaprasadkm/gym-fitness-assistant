from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from app.models.schemas import PerformanceReportOut
from app.database import get_supabase
from app.utils.security import get_current_user

router = APIRouter(prefix="/performance", tags=["Module 6: Pose-to-Performance Analyzer"])


@router.get("/weekly", response_model=PerformanceReportOut)
async def weekly_report(user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    week_start = datetime.now(timezone.utc) - timedelta(days=7)

    sessions_resp = (
        await supabase.table("workout_sessions")
        .select("form_score, tempo_consistency")
        .eq("user_id", user["id"])
        .gte("created_at", week_start.isoformat())
        .execute()
    )
    sessions = sessions_resp.data or []

    if not sessions:
        report = {
            "week_start": week_start.date().isoformat(),
            "total_sessions": 0,
            "avg_form_score": 0.0,
            "avg_tempo_consistency": 0.0,
            "performance_score": 0.0,
            "trend": "no data yet",
        }
    else:
        avg_form = sum(s.get("form_score", 0) for s in sessions) / len(sessions)
        avg_tempo = sum(s.get("tempo_consistency", 0) for s in sessions) / len(sessions)
        performance_score = round(0.6 * avg_form + 0.4 * avg_tempo, 1)

        prev_resp = (
            await supabase.table("performance_reports")
            .select("performance_score")
            .eq("user_id", user["id"])
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        prev_rows = prev_resp.data or []
        if prev_rows and prev_rows[0].get("performance_score") is not None:
            prev_score = prev_rows[0]["performance_score"]
            trend = "improving" if performance_score > prev_score else (
                "declining" if performance_score < prev_score else "steady"
            )
        else:
            trend = "first report"

        report = {
            "week_start": week_start.date().isoformat(),
            "total_sessions": len(sessions),
            "avg_form_score": round(avg_form, 1),
            "avg_tempo_consistency": round(avg_tempo, 1),
            "performance_score": performance_score,
            "trend": trend,
        }

    await supabase.table("performance_reports").insert({
        **report, "user_id": user["id"], "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()
    return report
