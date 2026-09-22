import streamlit as st
from utils.auth import current_user
from utils import api_client

user = current_user()
name = user.get("name", "there")

st.markdown(
    f"""
    <div style="padding: 1.5rem 1.75rem; border-radius: 16px;
                background: linear-gradient(135deg, rgba(34,197,94,0.18), rgba(34,197,94,0.03));
                border: 1px solid rgba(34,197,94,0.3); margin-bottom: 1.5rem;">
        <div style="font-size: 2rem;">👋 Welcome back, {name}!</div>
        <div style="color:#9CA3AF; margin-top:0.25rem;">
            Here's where things stand across your training, diet and habits.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Personal quick-stats row ----------
col1, col2, col3, col4 = st.columns(4)

try:
    perf = api_client.get_weekly_performance()
    col1.metric("Performance score", f"{perf['performance_score']}/100", help="This week's average across your workout sessions")
    col2.metric("Sessions this week", perf["total_sessions"])
except RuntimeError:
    col1.metric("Performance score", "—")
    col2.metric("Sessions this week", "—")

try:
    habit = api_client.get_habit_prediction()
    col3.metric("Current streak", f"{habit['current_streak']} 🔥")
    col4.metric("Skip risk", f"{habit['skip_risk_percent']}%")
except RuntimeError:
    col3.metric("Current streak", "—")
    col4.metric("Skip risk", "—")

st.divider()

try:
    diet = api_client.get_diet_plan()
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.metric("Target calories", f"{diet['target_calories']} kcal/day")
        c2.metric("BMI", f"{diet['bmi']} ({diet['bmi_category']})")
        c3.metric("Goal", user.get("goal", "—").capitalize())
except RuntimeError:
    st.info("Set up your diet plan on the **Diet** page to see your targets here.")

st.markdown("### Explore your modules")

modules = [
    ("🏋️ AI Gym Trainer", "Webcam pose detection, live rep counting & real-time form feedback."),
    ("🥗 AI Dietician & Calorie Coach", "BMI, BMR, macros, meal plan & grocery list."),
    ("📡 Smart Gym Assistant (AI + IoT)", "Simulated sensor feed drives resistance & rest recommendations."),
    ("🔥 AI Fitness Habit Tracker", "Skip-risk prediction, streaks & motivational nudges."),
    ("💬 Virtual Gym Buddy", "Mood-aware AI chat companion."),
    ("📈 Pose-to-Performance Analyzer", "Weekly performance score & trend from your sessions."),
    ("📍 Gym Recommender & Planner", "Nearby gyms matched to your goal - just type a place name."),
]

cols = st.columns(2)
for i, (title, desc) in enumerate(modules):
    with cols[i % 2]:
        with st.container(border=True):
            st.subheader(title)
            st.write(desc)
