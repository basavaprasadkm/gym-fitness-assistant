from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# ---------- Auth ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = "maintain"  # lose | gain | maintain


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfileOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = "maintain"
    is_admin: bool = False
    created_at: Optional[datetime] = None


# ---------- Module 1: AI Gym Trainer (workout / pose) ----------
class RepEvent(BaseModel):
    exercise: str                 # e.g. "squat", "bicep_curl", "pushup"
    joint_angle: float            # angle computed client-side by MediaPipe
    timestamp: Optional[datetime] = None


class WorkoutSessionIn(BaseModel):
    exercise: str
    reps: List[RepEvent] = []
    duration_seconds: float
    form_issues: List[str] = []   # e.g. ["knees caving in", "back not straight"]


class WorkoutSessionOut(WorkoutSessionIn):
    id: str
    user_id: str
    rep_count: int
    feedback: List[str]
    created_at: datetime


# ---------- Module 2: AI Dietician & Calorie Coach ----------
class DietRequest(BaseModel):
    weight_kg: float
    height_cm: float
    age: int
    sex: str                       # "male" | "female"
    activity_level: str            # sedentary|light|moderate|active|very_active
    goal: str                      # lose | gain | maintain
    dietary_preference: str = "veg"  # veg | non_veg | vegan


class DietPlanOut(BaseModel):
    bmi: float
    bmi_category: str
    bmr: float
    target_calories: float
    macros: dict
    meal_plan: dict
    grocery_list: List[str]


# ---------- Module 3: Smart Gym Assistant (AI + simulated IoT) ----------
class IoTReadingIn(BaseModel):
    heart_rate: int
    equipment: str
    current_resistance: int
    reps_completed: int


class IoTRecommendationOut(BaseModel):
    recommended_resistance: int
    recommended_rest_seconds: int
    intensity_status: str
    message: str


# ---------- Module 4: Habit Tracker (Behavioral AI) ----------
class HabitLogIn(BaseModel):
    date: str            # ISO date
    workout_completed: bool
    planned: bool = True


class HabitPredictionOut(BaseModel):
    skip_risk_percent: float
    current_streak: int
    nudge_message: str


# ---------- Module 5: Virtual Gym Buddy (chat) ----------
class ChatIn(BaseModel):
    message: str


class ChatOut(BaseModel):
    reply: str
    detected_mood: str


# ---------- Module 6: Pose-to-Performance Analyzer ----------
class PerformanceReportOut(BaseModel):
    week_start: str
    total_sessions: int
    avg_form_score: float
    avg_tempo_consistency: float
    performance_score: float
    trend: str


# ---------- Module 7: Gym Recommender & Planner ----------
class GymRecommendRequest(BaseModel):
    latitude: float
    longitude: float
    goal: Optional[str] = None
    max_distance_km: float = 10.0


class GymOut(BaseModel):
    name: str
    distance_km: float
    programs: List[str]
    rating: float
