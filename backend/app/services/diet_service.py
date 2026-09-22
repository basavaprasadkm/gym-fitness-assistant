"""
Module 2: AI Dietician & Calorie Coach.

Rule-based NLP-adjacent coach: it doesn't need a heavy LLM to recommend diet
plans - it uses standard sports-nutrition formulas (Mifflin-St Jeor BMR,
activity multipliers, goal-based calorie adjustment) plus templated meals per
dietary preference, then derives a grocery list from the chosen meals.
"""
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

MEAL_TEMPLATES = {
    "veg": {
        "breakfast": ["Oats with milk & banana", "2 boiled eggs substitute: paneer bhurji", "Mixed nuts"],
        "lunch": ["Brown rice", "Dal (lentils)", "Mixed vegetable curry", "Curd/yogurt"],
        "snack": ["Sprouts salad", "Fruit bowl"],
        "dinner": ["Roti (2-3)", "Paneer/tofu sabzi", "Salad"],
    },
    "non_veg": {
        "breakfast": ["Boiled eggs (2-3)", "Whole wheat toast", "Fruit"],
        "lunch": ["Brown rice", "Grilled chicken breast", "Sauteed vegetables"],
        "snack": ["Greek yogurt", "Almonds"],
        "dinner": ["Roti (2)", "Fish/chicken curry", "Salad"],
    },
    "vegan": {
        "breakfast": ["Oats with almond milk & berries", "Peanut butter toast"],
        "lunch": ["Quinoa/brown rice", "Chickpea curry", "Steamed vegetables"],
        "snack": ["Roasted chana", "Fruit"],
        "dinner": ["Roti (2-3)", "Tofu/soy chunk curry", "Salad"],
    },
}

GROCERY_MAP = {
    "veg": ["Oats", "Milk", "Bananas", "Paneer", "Mixed nuts", "Brown rice", "Lentils (dal)",
            "Seasonal vegetables", "Curd/yogurt", "Whole wheat flour (atta)", "Sprouts", "Fruits"],
    "non_veg": ["Eggs", "Whole wheat bread", "Fruits", "Brown rice", "Chicken breast", "Vegetables",
                "Greek yogurt", "Almonds", "Fish/chicken", "Whole wheat flour (atta)"],
    "vegan": ["Oats", "Almond milk", "Berries", "Peanut butter", "Whole wheat bread", "Quinoa/brown rice",
              "Chickpeas", "Vegetables", "Roasted chana", "Tofu/soy chunks", "Whole wheat flour (atta)", "Fruits"],
}


def calculate_bmi(weight_kg: float, height_cm: float) -> tuple[float, str]:
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category


def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    # Mifflin-St Jeor Equation
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex.lower() == "male" else base - 161


def build_diet_plan(weight_kg: float, height_cm: float, age: int, sex: str,
                     activity_level: str, goal: str, dietary_preference: str) -> dict:
    bmi, bmi_category = calculate_bmi(weight_kg, height_cm)
    bmr = calculate_bmr(weight_kg, height_cm, age, sex)
    maintenance = bmr * ACTIVITY_MULTIPLIERS.get(activity_level, 1.375)

    if goal == "lose":
        target_calories = maintenance - 500
    elif goal == "gain":
        target_calories = maintenance + 400
    else:
        target_calories = maintenance

    protein_g = round(weight_kg * (1.8 if goal == "gain" else 1.6))
    fat_kcal = target_calories * 0.25
    protein_kcal = protein_g * 4
    carb_kcal = target_calories - fat_kcal - protein_kcal

    macros = {
        "protein_g": protein_g,
        "fat_g": round(fat_kcal / 9),
        "carbs_g": round(carb_kcal / 4),
    }

    pref = dietary_preference if dietary_preference in MEAL_TEMPLATES else "veg"
    meal_plan = MEAL_TEMPLATES[pref]
    grocery_list = GROCERY_MAP[pref]

    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bmr": round(bmr, 1),
        "target_calories": round(target_calories),
        "macros": macros,
        "meal_plan": meal_plan,
        "grocery_list": grocery_list,
    }
