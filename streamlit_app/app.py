import streamlit as st
from utils.auth import require_login, logout_button, is_admin

st.set_page_config(page_title="AI Gym & Fitness Assistant", page_icon="🏋️", layout="wide")

st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background: rgba(148, 163, 184, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 0.9rem 1rem 0.6rem;
    }
    div[data-testid="stMetricLabel"] { font-size: 0.85rem; opacity: 0.8; }
    section[data-testid="stSidebar"] button[kind="secondary"] { border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Login/register gate - runs before any page is shown. Individual page files
# under views/ do NOT call require_login()/logout_button() themselves
# anymore; this is the single place that owns both, and st.set_page_config()
# must only be called once per app, right here.
require_login()
logout_button()

# Filenames stay plain ASCII on purpose (emoji filenames get corrupted when
# a zip is extracted with certain Windows tools - the icons below are the
# supported way to show emoji in the sidebar without touching filenames).
pages = [
    st.Page("views/0_Home.py", title="Home", icon="🏠"),
    st.Page("views/1_Workout.py", title="Workout", icon="🏋️"),
    st.Page("views/2_Diet.py", title="Diet", icon="🥗"),
    st.Page("views/3_Smart_Gym.py", title="Smart Gym", icon="📡"),
    st.Page("views/4_Habit.py", title="Habit", icon="🔥"),
    st.Page("views/5_Chat.py", title="Chat", icon="💬"),
    st.Page("views/6_Performance.py", title="Performance", icon="📈"),
    st.Page("views/7_Gym_Finder.py", title="Gym Finder", icon="📍"),
]

# Admin page only appears in the sidebar for accounts with is_admin = true
# (promoted via SQL - see supabase_migration_admin.sql). A non-admin user
# also can't reach it directly: every /admin/* backend endpoint independently
# re-checks is_admin on the server side, so hiding the nav link is a
# convenience, not the actual access control.
if is_admin():
    pages.append(st.Page("views/8_Admin.py", title="Admin", icon="🛠️"))

pg = st.navigation(pages)
pg.run()
