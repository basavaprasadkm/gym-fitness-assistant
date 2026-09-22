import streamlit as st
from utils import api_client

st.title("💬 Virtual Gym Buddy")
st.caption("Tell it how you're feeling - it detects your mood and responds accordingly.")

if "chat_loaded" not in st.session_state:
    try:
        history = api_client.get_chat_history()
        st.session_state["chat_messages"] = [
            {"message": h["message"], "reply": h["reply"], "mood": h["mood"]} for h in reversed(history)
        ]
    except RuntimeError:
        st.session_state["chat_messages"] = []
    st.session_state["chat_loaded"] = True

for turn in st.session_state["chat_messages"]:
    with st.chat_message("user"):
        st.write(turn["message"])
    with st.chat_message("assistant"):
        st.write(f"{turn['reply']}  \n:gray[({turn['mood']})]")

user_input = st.chat_input("How are you feeling about today's workout?")
if user_input:
    try:
        result = api_client.send_chat_message(user_input)
        st.session_state["chat_messages"].append({
            "message": user_input, "reply": result["reply"], "mood": result["detected_mood"],
        })
        st.rerun()
    except RuntimeError as e:
        st.error(str(e))
