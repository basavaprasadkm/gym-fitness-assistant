from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_supabase
from app.routers import auth, workout, diet, iot, habit, chatbot, performance, recommender, admin
from app.services.recommender_service import ensure_seeded


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_supabase()
    await ensure_seeded()  # seeds the mock gym directory once, if empty
    yield


app = FastAPI(
    title="AI Gym & Fitness Assistant",
    description="Unified AI fitness ecosystem: workout detection, diet planning, "
                "simulated smart-gym IoT, habit tracking, a chat companion, "
                "performance analytics, and gym recommendations. Backed by Supabase (Postgres).",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.FRONTEND_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workout.router)
app.include_router(diet.router)
app.include_router(iot.router)
app.include_router(habit.router)
app.include_router(chatbot.router)
app.include_router(performance.router)
app.include_router(recommender.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "AI Gym & Fitness Assistant API is running (Supabase-backed)",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
