"""
Module 3: Smart Gym Assistant (AI + IoT Integration) - simulated per the
project brief ("no need of any physical IoT implementation").

In a real deployment this data would come from a smartwatch/gym-machine
sensor over MQTT. Here /iot/simulate generates a realistic reading so the
whole pipeline (sensor -> AI decision -> UI) can be demoed end-to-end, and
/iot/recommend accepts either simulated or manually entered readings and runs
the same decision logic a real integration would use.
"""
import random

# Heart-rate zone thresholds are a simplification of the classic
# % of max-heart-rate training zones.
def recommend(heart_rate: int, current_resistance: int, reps_completed: int, age: int = 25) -> dict:
    max_hr = 220 - age
    hr_percent = heart_rate / max_hr * 100

    if hr_percent >= 90:
        resistance_delta = -2
        rest = 90
        status = "Over-exertion risk"
        message = "Heart rate is very high - lowering resistance and extending rest."
    elif hr_percent >= 75:
        resistance_delta = 0
        rest = 60
        status = "Optimal intensity"
        message = "You're in a great training zone - hold this resistance."
    elif hr_percent >= 55:
        resistance_delta = 1
        rest = 45
        status = "Under-loaded"
        message = "Heart rate is low for this stage - resistance increased slightly."
    else:
        resistance_delta = 2
        rest = 30
        status = "Warm-up zone"
        message = "Still warming up - resistance bumped up to build intensity."

    recommended_resistance = max(1, current_resistance + resistance_delta)

    if reps_completed >= 15:
        rest += 15
        message += " Also extending rest slightly since you've done a high-rep set."

    return {
        "recommended_resistance": recommended_resistance,
        "recommended_rest_seconds": rest,
        "intensity_status": status,
        "message": message,
    }


def simulate_reading(equipment: str = "treadmill") -> dict:
    """Generates a plausible sensor reading to stand in for real IoT hardware."""
    return {
        "heart_rate": random.randint(95, 175),
        "equipment": equipment,
        "current_resistance": random.randint(3, 10),
        "reps_completed": random.randint(0, 20),
    }
