from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.models.schemas import DietRequest, DietPlanOut
from app.database import get_supabase
from app.utils.security import get_current_user
from app.services.diet_service import build_diet_plan

router = APIRouter(prefix="/diet", tags=["Module 2: AI Dietician & Calorie Coach"])


@router.post("/plan", response_model=DietPlanOut)
async def generate_plan(req: DietRequest, user: dict = Depends(get_current_user)):
    plan = build_diet_plan(
        weight_kg=req.weight_kg,
        height_cm=req.height_cm,
        age=req.age,
        sex=req.sex,
        activity_level=req.activity_level,
        goal=req.goal,
        dietary_preference=req.dietary_preference,
    )

    supabase = get_supabase()
    doc = {**plan, "user_id": user["id"], "updated_at": datetime.now(timezone.utc).isoformat()}
    # one diet plan per user - upsert on the unique user_id column
    await supabase.table("diet_plans").upsert(doc, on_conflict="user_id").execute()
    return plan


@router.get("/plan", response_model=DietPlanOut)
async def get_latest_plan(user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    resp = await supabase.table("diet_plans").select("*").eq("user_id", user["id"]).maybe_single().execute()

    if not resp or not resp.data:
        return await generate_plan(
            DietRequest(
                weight_kg=user.get("weight_kg") or 70,
                height_cm=user.get("height_cm") or 170,
                age=user.get("age") or 25,
                sex="male",
                activity_level="moderate",
                goal=user.get("goal") or "maintain",
                dietary_preference="veg",
            ),
            user,
        )
    return resp.data
