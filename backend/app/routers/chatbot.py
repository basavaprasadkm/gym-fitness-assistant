from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends

from app.models.schemas import ChatIn, ChatOut
from app.database import get_supabase
from app.utils.security import get_current_user
from app.services.chat_service import generate_reply

router = APIRouter(prefix="/chat", tags=["Module 5: Virtual Gym Buddy"])


@router.post("/message", response_model=ChatOut)
async def send_message(chat: ChatIn, user: dict = Depends(get_current_user)):
    result = generate_reply(chat.message)

    supabase = get_supabase()
    await supabase.table("chat_history").insert({
        "user_id": user["id"],
        "message": chat.message,
        "reply": result["reply"],
        "mood": result["detected_mood"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()
    return result


@router.get("/history")
async def get_chat_history(user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    resp = (
        await supabase.table("chat_history")
        .select("*")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    return resp.data
