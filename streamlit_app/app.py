import streamlit as st

# Page configuration must be called exactly once and before other
# Streamlit commands.
st.set_page_config(
    page_title="AI Gym & Fitness Assistant",
    page_icon="🏋️",
    layout="wide"
)

from utils.auth import require_login, logout_button, is_admin


st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background: rgba(148, 163, 184, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 0.9rem 1rem 0.6rem;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        opacity: 0.8;
    }

    section[data-testid="stSidebar"] button[kind="secondary"] {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Login/register gate - runs before any page is shown.
# Individual page files under views/ do NOT call require_login()
# or logout_button() themselves.
require_login()
logout_button()


# Filenames stay plain ASCII on purpose.
# Emoji are used only as sidebar icons.
pages = [
    st.Page(
        "views/0_Home.py",
        title="Home",
        icon="🏠"
    ),
    st.Page(
        "views/1_Workout.py",
        title="Workout",
        icon="🏋️"
    ),
    st.Page(
        "views/2_Diet.py",
        title="Diet",
        icon="🥗"
    ),
    st.Page(
        "views/3_Smart_Gym.py",
        title="Smart Gym",
        icon="📡"
    ),
    st.Page(
        "views/4_Habit.py",
        title="Habit",
        icon="🔥"
    ),
    st.Page(
        "views/5_Chat.py",
        title="Chat",
        icon="💬"
    ),
    st.Page(
        "views/6_Performance.py",
        title="Performance",
        icon="📈"
    ),
    st.Page(
        "views/7_Gym_Finder.py",
        title="Gym Finder",
        icon="📍"
    ),
]


# Admin page only appears for admin accounts.
# Backend endpoints must still verify admin permissions.
if is_admin():
    pages.append(
        st.Page(
            "views/8_Admin.py",
            title="Admin",
            icon="🛠️"
        )
    )


# Create and run the Streamlit navigation.
pg = st.navigation(pages)
pg.run()

