"""
Shared login/register gate. Every module page calls require_login() at the
top - it renders a login/register form and st.stop()s the script if the user
isn't authenticated yet, so the rest of that page's code never runs.

Also fetches and caches the user's own profile (name, is_admin, etc.) right
after login/register via GET /auth/me, so:
  - the sidebar and Home dashboard can greet the user by name without an
    extra API call on every page, and
  - app.py can decide whether to show the Admin page in navigation, based
    on session_state["profile"]["is_admin"].
"""
import streamlit as st
from utils import api_client


def current_user() -> dict:
    """The logged-in user's cached profile (empty dict if not loaded yet)."""
    return st.session_state.get("profile") or {}


def is_admin() -> bool:
    return bool(current_user().get("is_admin"))


def _load_profile() -> bool:
    try:
        st.session_state["profile"] = api_client.get_me()
        return True
    except RuntimeError:
        # token expired/invalid - drop it and fall back to the login screen
        st.session_state.pop("token", None)
        st.session_state.pop("profile", None)
        return False


def require_login():
    if st.session_state.get("token"):
        if st.session_state.get("profile") or _load_profile():
            return  # already logged in with a cached profile - let the page continue

    st.markdown(
        """
        <div style="text-align:center; padding: 1.5rem 0 0.5rem;">
            <div style="font-size:3rem;">🏋️</div>
            <h1 style="margin-bottom:0;">AI Gym & Fitness Assistant</h1>
            <p style="color:#9CA3AF;">Your all-in-one AI-powered training, diet and motivation coach</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([1, 2, 1])
    with center:
        tab_login, tab_register = st.tabs(["🔐 Log in", "📝 Register"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log in", use_container_width=True)
            if submitted:
                try:
                    result = api_client.login(email, password)
                    st.session_state["token"] = result["access_token"]
                    _load_profile()
                    st.rerun()
                except RuntimeError as e:
                    st.error(str(e))

        with tab_register:
            with st.form("register_form"):
                name = st.text_input("Name")
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                col1, col2, col3 = st.columns(3)
                age = col1.number_input("Age", min_value=0, max_value=120, value=25)
                height_cm = col2.number_input("Height (cm)", min_value=0.0, value=170.0)
                weight_kg = col3.number_input("Weight (kg)", min_value=0.0, value=70.0)
                goal = st.selectbox("Goal", ["lose", "maintain", "gain"])
                reg_submitted = st.form_submit_button("Create account", use_container_width=True)
            if reg_submitted:
                try:
                    result = api_client.register({
                        "name": name, "email": reg_email, "password": reg_password,
                        "age": int(age), "height_cm": height_cm, "weight_kg": weight_kg, "goal": goal,
                    })
                    st.session_state["token"] = result["access_token"]
                    _load_profile()
                    st.rerun()
                except RuntimeError as e:
                    st.error(str(e))

    st.stop()


def logout_button():
    profile = current_user()
    if profile.get("name"):
        badge = " 👑" if profile.get("is_admin") else ""
        st.sidebar.markdown(f"**{profile['name']}**{badge}")
        st.sidebar.caption(profile.get("email", ""))
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.pop("token", None)
        st.session_state.pop("profile", None)
        st.rerun()
    st.sidebar.divider()
