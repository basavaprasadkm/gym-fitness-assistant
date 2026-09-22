import streamlit as st
from utils import api_client

st.title("🥗 AI Dietician & Calorie Coach")
st.caption("BMI/BMR-based calorie target, macros, meal plan and grocery list.")

with st.form("diet_form"):
    c1, c2, c3 = st.columns(3)
    weight_kg = c1.number_input("Weight (kg)", min_value=1.0, value=70.0)
    height_cm = c2.number_input("Height (cm)", min_value=1.0, value=170.0)
    age = c3.number_input("Age", min_value=1, max_value=120, value=25)

    c4, c5, c6 = st.columns(3)
    sex = c4.selectbox("Sex", ["male", "female"])
    activity_level = c5.selectbox(
        "Activity level", ["sedentary", "light", "moderate", "active", "very_active"], index=2,
    )
    goal = c6.selectbox("Goal", ["lose", "maintain", "gain"], index=1)

    dietary_preference = st.selectbox("Dietary preference", ["veg", "non_veg", "vegan"])
    submitted = st.form_submit_button("Generate Plan")

if submitted:
    try:
        plan = api_client.generate_diet_plan({
            "weight_kg": weight_kg, "height_cm": height_cm, "age": int(age),
            "sex": sex, "activity_level": activity_level, "goal": goal,
            "dietary_preference": dietary_preference,
        })
        st.session_state["diet_plan"] = plan
    except RuntimeError as e:
        st.error(str(e))

plan = st.session_state.get("diet_plan")
if plan:
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("BMI", f"{plan['bmi']} ({plan['bmi_category']})")
        c2.metric("BMR", f"{plan['bmr']} kcal")
        c3.metric("Target calories", f"{plan['target_calories']} kcal/day")

        st.write(
            f"**Macros:** {plan['macros']['protein_g']}g protein · "
            f"{plan['macros']['carbs_g']}g carbs · {plan['macros']['fat_g']}g fat"
        )

        st.subheader("Meal Plan")
        for meal, items in plan["meal_plan"].items():
            st.write(f"**{meal.capitalize()}:** {', '.join(items)}")

        st.subheader("Grocery List")
        cols = st.columns(2)
        half = (len(plan["grocery_list"]) + 1) // 2
        for i, item in enumerate(plan["grocery_list"]):
            cols[0 if i < half else 1].write(f"- {item}")
