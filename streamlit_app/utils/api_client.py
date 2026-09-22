"""
Thin wrapper around the FastAPI backend (see ../backend). Every module page
calls through here instead of hitting `requests` directly, so the auth
header and error handling live in exactly one place. Every function here
raises a plain RuntimeError on ANY failure (HTTP error response, backend
unreachable, timeout, etc.) so pages only ever need one except clause.
"""
import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")


def _headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _request(method: str, path: str, **kwargs):
    try:
        resp = requests.request(method, f"{API_URL}{path}", timeout=15, **kwargs)
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Can't reach the backend at {API_URL}. Is it running? (uvicorn app.main:app --reload)"
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError("The backend took too long to respond.") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(str(e)) from e

    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise RuntimeError(detail)
    return resp.json() if resp.content else None


# ---------- Auth ----------
def register(payload: dict):
    return _request("POST", "/auth/register", json=payload)


def login(email: str, password: str):
    return _request("POST", "/auth/login", json={"email": email, "password": password})


def get_me():
    return _request("GET", "/auth/me", headers=_headers())


# ---------- Module 1: Workout ----------
def submit_workout_session(payload: dict):
    return _request("POST", "/workout/session", json=payload, headers=_headers())


def get_workout_history():
    return _request("GET", "/workout/history", headers=_headers())


# ---------- Module 2: Diet ----------
def generate_diet_plan(payload: dict):
    return _request("POST", "/diet/plan", json=payload, headers=_headers())


def get_diet_plan():
    return _request("GET", "/diet/plan", headers=_headers())


# ---------- Module 3: Smart Gym / IoT ----------
def simulate_iot_reading(equipment: str):
    return _request("GET", "/iot/simulate", params={"equipment": equipment})


def get_iot_recommendation(payload: dict):
    return _request("POST", "/iot/recommend", json=payload, headers=_headers())


# ---------- Module 4: Habit ----------
def log_habit(payload: dict):
    return _request("POST", "/habit/log", json=payload, headers=_headers())


def get_habit_prediction():
    return _request("GET", "/habit/prediction", headers=_headers())


# ---------- Module 5: Chat ----------
def send_chat_message(message: str):
    return _request("POST", "/chat/message", json={"message": message}, headers=_headers())


def get_chat_history():
    return _request("GET", "/chat/history", headers=_headers())


# ---------- Module 6: Performance ----------
def get_weekly_performance():
    return _request("GET", "/performance/weekly", headers=_headers())


# ---------- Module 7: Gym Recommender ----------
def geocode_place(query: str):
    return _request("GET", "/gyms/geocode", params={"query": query}, headers=_headers())


def recommend_gyms(payload: dict):
    return _request("POST", "/gyms/recommend", json=payload, headers=_headers())


# ---------- Admin ----------
def admin_list_users():
    return _request("GET", "/admin/users", headers=_headers())


def admin_overview():
    return _request("GET", "/admin/overview", headers=_headers())


def admin_user_activity(user_id: str):
    return _request("GET", f"/admin/users/{user_id}/activity", headers=_headers())
