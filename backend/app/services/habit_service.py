"""
Module 4: AI Fitness Habit Tracker (Behavioral AI).

Predicts skip risk from recent adherence history (a lightweight, explainable
stand-in for a trained behavioral model - it weights recent days more heavily
than older ones, which is the same idea a logistic-regression-on-recency
model would learn, without needing a training pipeline for a portfolio demo).
"""
from datetime import datetime, date
from typing import List


def compute_streak(logs: List[dict]) -> int:
    """Consecutive most-recent days where a planned workout was completed."""
    streak = 0
    for log in sorted(logs, key=lambda x: x["date"], reverse=True):
        if log.get("planned", True) and log.get("workout_completed"):
            streak += 1
        elif log.get("planned", True):
            break
    return streak


def predict_skip_risk(logs: List[dict]) -> float:
    if not logs:
        return 50.0

    recent = sorted(logs, key=lambda x: x["date"], reverse=True)[:14]
    total_weight = 0.0
    missed_weight = 0.0
    for i, log in enumerate(recent):
        if not log.get("planned", True):
            continue
        weight = 1 / (i + 1)  # more recent days count more
        total_weight += weight
        if not log.get("workout_completed"):
            missed_weight += weight

    if total_weight == 0:
        return 50.0
    risk = round((missed_weight / total_weight) * 100, 1)
    return risk


def build_nudge(skip_risk: float, streak: int) -> str:
    if streak >= 5:
        return f"🔥 {streak}-day streak! You're on fire - don't break the chain today."
    if skip_risk >= 60:
        return "We've noticed you've been skipping lately. Even a 10-minute session keeps momentum going!"
    if skip_risk >= 30:
        return "Your consistency has dipped a bit - let's get back on track with today's session."
    return "You're doing great - keep showing up!"
