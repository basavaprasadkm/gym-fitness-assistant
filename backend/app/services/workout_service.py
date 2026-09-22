"""
Module 1 (AI Gym Trainer) + Module 6 (Pose-to-Performance Analyzer) logic.

Real-time pose landmark extraction happens client-side in the browser using
MediaPipe Pose (see frontend/src/pages/Workout.jsx). The frontend computes a
joint angle for each rep (e.g. knee angle for squats, elbow angle for curls)
and streams RepEvents here. This keeps the heavy CV work off a Python server
(no GPU needed) while still doing genuine pose-based analysis.

This module is the "brain" that turns those raw angles into:
  - a validated rep count
  - real-time form feedback
  - a 0-100 form score and tempo-consistency score used by the
    Pose-to-Performance Analyzer for weekly reports.
"""
from statistics import pstdev
from typing import List
from app.models.schemas import RepEvent

# Ideal joint-angle ranges (degrees) at the bottom of the movement, per exercise.
# A rep only "counts" if the angle actually reaches the target range - this is
# what prevents partial reps from inflating the count.
EXERCISE_RANGES = {
    "squat": (70, 100),        # knee angle at bottom of squat
    "pushup": (70, 100),       # elbow angle at bottom of pushup
    "bicep_curl": (30, 60),    # elbow angle at top of curl
    "lunge": (80, 110),        # front knee angle
    "shoulder_press": (150, 180),
}


def analyze_session(exercise: str, reps: List[RepEvent], duration_seconds: float,
                     form_issues: List[str]) -> dict:
    exercise = exercise.lower()
    low, high = EXERCISE_RANGES.get(exercise, (0, 180))

    valid_reps = [r for r in reps if low <= r.joint_angle <= high]
    rep_count = len(valid_reps)
    total_attempted = len(reps)

    # Form score: proportion of attempted reps that hit the correct range,
    # penalized further for each distinct form issue flagged by pose analysis.
    range_accuracy = (rep_count / total_attempted * 100) if total_attempted else 0
    form_score = max(0, round(range_accuracy - 5 * len(set(form_issues)), 1))

    # Tempo consistency: lower variance in time between reps = more consistent
    # control (vs. rushing some reps and pausing on others).
    timestamps = [r.timestamp for r in reps if r.timestamp]
    tempo_consistency = 100.0
    if len(timestamps) >= 3:
        deltas = [(timestamps[i] - timestamps[i - 1]).total_seconds() for i in range(1, len(timestamps))]
        deltas = [d for d in deltas if d > 0]
        if deltas:
            spread = pstdev(deltas)
            avg = sum(deltas) / len(deltas)
            tempo_consistency = max(0, round(100 - (spread / avg * 100 if avg else 0), 1))

    feedback = []
    if total_attempted and rep_count < total_attempted:
        feedback.append(
            f"{total_attempted - rep_count} rep(s) didn't reach full range of motion - go deeper/slower."
        )
    if form_score >= 85:
        feedback.append("Great form! Keep this consistency.")
    elif form_score >= 60:
        feedback.append("Decent form, but watch your range of motion on some reps.")
    else:
        feedback.append("Form needs work - consider reducing weight/speed and focusing on technique.")

    for issue in set(form_issues):
        feedback.append(f"Correction: {issue}.")

    return {
        "rep_count": rep_count,
        "feedback": feedback,
        "form_score": form_score,
        "tempo_consistency": tempo_consistency,
    }
