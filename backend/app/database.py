"""
Async Supabase (Postgres) client, shared across the whole app.

The client is created once during FastAPI's startup (see main.py's lifespan
handler) because `create_async_client` is itself a coroutine. Every
router/service imports `get_supabase()` and calls it lazily rather than
importing a client instance directly, so it always gets the initialized
client regardless of import order.

Table names (mirroring the old Mongo collection names for anyone diffing
against the previous version):
  users               - accounts + profile fields
  workout_sessions    - Module 1 & 6: rep logs, pose scores
  diet_plans          - Module 2 (one row per user, upserted)
  iot_readings        - Module 3: simulated sensor data + AI recommendation
  habit_logs          - Module 4: one row per user per day
  chat_history        - Module 5: virtual buddy conversation log
  performance_reports - Module 6: weekly aggregate snapshots
  gyms                - Module 7: seeded mock gym directory
"""
from supabase import create_async_client, AsyncClient
from app.config import settings

_supabase: AsyncClient | None = None


async def init_supabase() -> AsyncClient:
    global _supabase
    _supabase = await create_async_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase


def get_supabase() -> AsyncClient:
    if _supabase is None:
        raise RuntimeError(
            "Supabase client not initialized yet - this should only happen if a "
            "request comes in before the app's startup/lifespan handler has run."
        )
    return _supabase
