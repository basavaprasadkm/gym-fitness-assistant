import streamlit as st
from utils import api_client

st.title("📡 Smart Gym Assistant (AI + IoT)")
st.caption(
    "No physical hardware needed for this demo - a sensor reading is simulated, then the AI "
    "decides resistance and rest time exactly as it would with a real connected machine."
)

equipment = st.selectbox(
    "Equipment", ["treadmill", "rowing_machine", "stationary_bike", "resistance_machine"],
)

if st.button("Get Sensor Reading"):
    st.session_state["iot_reading"] = api_client.simulate_iot_reading(equipment)
    st.session_state.pop("iot_recommendation", None)

reading = st.session_state.get("iot_reading")
if reading:
    with st.container(border=True):
        st.subheader("Simulated Sensor Reading")
        c1, c2, c3 = st.columns(3)
        c1.metric("Heart rate", f"{reading['heart_rate']} bpm")
        c2.metric("Resistance", reading["current_resistance"])
        c3.metric("Reps completed", reading["reps_completed"])

        if st.button("Get AI Recommendation"):
            try:
                st.session_state["iot_recommendation"] = api_client.get_iot_recommendation(reading)
            except RuntimeError as e:
                st.error(str(e))

rec = st.session_state.get("iot_recommendation")
if rec:
    with st.container(border=True):
        st.subheader("AI Recommendation")
        st.write(f"**Status:** {rec['intensity_status']}")
        c1, c2 = st.columns(2)
        c1.metric("Recommended resistance", rec["recommended_resistance"])
        c2.metric("Recommended rest", f"{rec['recommended_rest_seconds']}s")
        st.write(rec["message"])
