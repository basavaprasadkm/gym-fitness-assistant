import streamlit as st
from utils import api_client

st.title("📍 Gym Recommender & Planner")
st.caption("Type a place name and get gyms nearby, matched to your fitness goal.")

with st.form("location_form"):
    place = st.text_input(
        "Location", placeholder="e.g. Koramangala, Bengaluru",
        help="Any place name works - a neighborhood, city, or landmark.",
    )
    col1, col2 = st.columns(2)
    goal = col1.selectbox("Goal", ["", "lose", "gain", "maintain", "strength", "cardio"])
    max_distance_km = col2.slider("Max distance (km)", min_value=1, max_value=50, value=10)
    search_submitted = st.form_submit_button("🔍 Find Gyms", use_container_width=True)

if search_submitted:
    if not place.strip():
        st.warning("Enter a place name first.")
    else:
        try:
            with st.spinner(f"Locating '{place}'..."):
                location = api_client.geocode_place(place)
            st.session_state["gym_location"] = location

            with st.spinner("Finding nearby gyms..."):
                gyms = api_client.recommend_gyms({
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "goal": goal or None,
                    "max_distance_km": max_distance_km,
                })
            st.session_state["gym_results"] = gyms
        except RuntimeError as e:
            st.error(str(e))
            st.session_state.pop("gym_results", None)

location = st.session_state.get("gym_location")
if location:
    st.success(f"📍 Showing gyms near **{location['display_name']}**")

results = st.session_state.get("gym_results")
if results:
    for gym in results:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.subheader(gym["name"])
                st.write(f"Programs: {', '.join(gym['programs'])}")
            with c2:
                st.metric("Distance", f"{gym['distance_km']} km")
                st.write(f"⭐ {gym['rating']}")
elif search_submitted:
    st.info("No gyms found within that distance - try increasing the max distance.")
