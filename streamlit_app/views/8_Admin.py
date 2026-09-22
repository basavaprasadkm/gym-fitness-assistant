"""
Admin dashboard - only reachable if app.py added it to navigation, which
only happens when the logged-in user's cached profile has is_admin = true.
Every call here still goes through /admin/* endpoints, which independently
re-check is_admin server-side (see backend/app/utils/security.py's
get_current_admin) - so this page being hidden from non-admins is a
convenience, not the actual security boundary.
"""
import streamlit as st
from utils import api_client

st.title("🛠️ Admin Dashboard")
st.caption("Platform-wide view across every registered user.")

try:
    overview = api_client.admin_overview()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total users", overview["total_users"])
c2.metric("Workout sessions", overview["total_workout_sessions"])
c3.metric("Chat messages", overview["total_chat_messages"])
c4.metric("Diet plans generated", overview["total_diet_plans"])
c5.metric("Platform avg form score", f"{overview['platform_avg_form_score']}/100")

st.divider()
st.markdown("### All users")

try:
    users = api_client.admin_list_users()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

if not users:
    st.info("No users registered yet.")
    st.stop()

st.dataframe(
    [
        {
            "Name": u["name"],
            "Email": u["email"],
            "Age": u.get("age") or "—",
            "Height (cm)": u.get("height_cm") or "—",
            "Weight (kg)": u.get("weight_kg") or "—",
            "Goal": u.get("goal") or "—",
            "Admin": "👑" if u.get("is_admin") else "",
            "Joined": (u.get("created_at") or "")[:10],
        }
        for u in users
    ],
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.markdown("### Drill into a user")

labels = {f"{u['name']} ({u['email']})": u["id"] for u in users}
selected_label = st.selectbox("Select a user", list(labels.keys()))
selected_id = labels[selected_label]

if st.button("Load activity"):
    try:
        activity = api_client.admin_user_activity(selected_id)
        st.session_state["admin_selected_activity"] = activity
    except RuntimeError as e:
        st.error(str(e))

activity = st.session_state.get("admin_selected_activity")
if activity:
    profile = activity["profile"]
    st.subheader(f"{profile['name']}'s activity")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Recent workout sessions**")
        if activity["recent_workouts"]:
            st.dataframe(
                [
                    {
                        "Exercise": w["exercise"],
                        "Reps": w["rep_count"],
                        "Form score": w["form_score"],
                        "Date": (w.get("created_at") or "")[:10],
                    }
                    for w in activity["recent_workouts"]
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No workout sessions logged yet.")

        st.markdown("**Latest performance report**")
        perf = activity["latest_performance"]
        if perf:
            st.metric("Performance score", f"{perf['performance_score']}/100")
        else:
            st.caption("No performance report yet.")

    with col2:
        st.markdown("**Recent habit logs**")
        if activity["recent_habit_logs"]:
            completed = sum(1 for h in activity["recent_habit_logs"] if h["workout_completed"])
            st.caption(f"{completed} of {len(activity['recent_habit_logs'])} recent planned days completed")
            st.dataframe(
                [{"Date": h["date"], "Completed": "✅" if h["workout_completed"] else "❌"} for h in activity["recent_habit_logs"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No habit logs yet.")

        st.markdown("**Diet plan**")
        diet = activity["diet_plan"]
        if diet:
            st.write(f"Target: **{diet['target_calories']} kcal/day** · BMI **{diet['bmi']}** ({diet['bmi_category']})")
        else:
            st.caption("No diet plan generated yet.")
