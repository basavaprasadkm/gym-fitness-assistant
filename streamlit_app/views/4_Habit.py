from datetime import date

import streamlit as st
from utils import api_client

st.title("🔥 AI Fitness Habit Tracker")
st.caption("Behavioral AI that predicts skip risk from your recent adherence and nudges you accordingly.")

today = date.today().isoformat()

c1, c2 = st.columns(2)
if c1.button("✅ I worked out today"):
    api_client.log_habit({"date": today, "workout_completed": True, "planned": True})
    st.success("Logged today's workout!")
if c2.button("⏭️ I skipped today"):
    api_client.log_habit({"date": today, "workout_completed": False, "planned": True})
    st.info("Logged a skipped day - no judgment, just data.")

try:
    prediction = api_client.get_habit_prediction()
    with st.container(border=True):
        st.subheader("Your Habit Snapshot")
        c1, c2 = st.columns(2)
        c1.metric("Current streak", f"{prediction['current_streak']} day(s)")
        c2.metric("Skip risk", f"{prediction['skip_risk_percent']}%")
        st.write(f"💬 {prediction['nudge_message']}")
except RuntimeError as e:
    st.error(str(e))
