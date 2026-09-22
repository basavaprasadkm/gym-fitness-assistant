import streamlit as st
from utils import api_client

st.title("📈 Pose-to-Performance Analyzer")
st.caption("Aggregates this week's AI Gym Trainer sessions into a single performance score.")

try:
    report = api_client.get_weekly_performance()
    with st.container(border=True):
        st.write(f"Week starting: **{report['week_start']}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Sessions logged", report["total_sessions"])
        c2.metric("Avg form score", f"{report['avg_form_score']}/100")
        c3.metric("Avg tempo consistency", f"{report['avg_tempo_consistency']}/100")
        st.metric("Performance Score", f"{report['performance_score']}/100")
        st.write(f"Trend: **{report['trend']}**")
        if report["total_sessions"] == 0:
            st.info("Complete a session in the AI Gym Trainer to see your score here.")
except RuntimeError as e:
    st.error(str(e))
