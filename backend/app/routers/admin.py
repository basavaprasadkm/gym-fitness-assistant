"""
Admin dashboard endpoints - everything here requires get_current_admin,
which rejects any non-admin user with a 403. There's no "admin" concept in
Supabase Auth here since this app uses its own JWT auth; admin status is
just an is_admin boolean on the users row, promoted manually via SQL
(see supabase_migration_admin.sql) rather than through the API, so a normal
user can never grant themselves admin access through the app itself.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_supabase
from app.utils.security import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

_PUBLIC_USER_COLUMNS = "id,name,email,age,height_cm,weight_kg,goal,is_admin,created_at"


@router.get("/users")
async def list_users(admin: dict = Depends(get_current_admin)):
    supabase = get_supabase()
    resp = (
        await supabase.table("users")
        .select(_PUBLIC_USER_COLUMNS)
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []


@router.get("/overview")
async def platform_overview(admin: dict = Depends(get_current_admin)):
    supabase = get_supabase()

    users = await supabase.table("users").select("id").execute()
    workouts = await supabase.table("workout_sessions").select("id,form_score").execute()
    chats = await supabase.table("chat_history").select("id").execute()
    diets = await supabase.table("diet_plans").select("id").execute()

    workout_rows = workouts.data or []
    avg_form_score = (
        round(sum(w.get("form_score") or 0 for w in workout_rows) / len(workout_rows), 1)
        if workout_rows else 0.0
    )

    return {
        "total_users": len(users.data or []),
        "total_workout_sessions": len(workout_rows),
        "total_chat_messages": len(chats.data or []),
        "total_diet_plans": len(diets.data or []),
        "platform_avg_form_score": avg_form_score,
    }


@router.get("/users/{user_id}/activity")
async def user_activity(user_id: str, admin: dict = Depends(get_current_admin)):
    supabase = get_supabase()

    user_resp = await supabase.table("users").select(_PUBLIC_USER_COLUMNS).eq("id", user_id).maybe_single().execute()
    profile = user_resp.data if user_resp else None
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")

    workouts = (
        await supabase.table("workout_sessions").select("*")
        .eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
    )
    habit_logs = (
        await supabase.table("habit_logs").select("*")
        .eq("user_id", user_id).order("date", desc=True).limit(30).execute()
    )
    latest_perf = (
        await supabase.table("performance_reports").select("*")
        .eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
    )
    diet_resp = await supabase.table("diet_plans").select("*").eq("user_id", user_id).maybe_single().execute()

    latest_perf_rows = latest_perf.data or []

    return {
        "profile": profile,
        "recent_workouts": workouts.data or [],
        "recent_habit_logs": habit_logs.data or [],
        "latest_performance": latest_perf_rows[0] if latest_perf_rows else None,
        "diet_plan": diet_resp.data if diet_resp else None,
    }
