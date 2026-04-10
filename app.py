import streamlit as st
import time
from brain import (
    get_carebot_response,
    summarize_symptoms,
    listen_to_user,
)

st.set_page_config(page_title="CareBot AI", page_icon="🩺", layout="wide")

st.markdown("""
<style>
.main { background-color: #f8f9fa; }

[data-testid="stSidebar"] {
    border-right: 1px solid #dee2e6;
}

.stChatMessage {
    border-radius: 12px;
    margin-bottom: 10px;
    padding: 6px;
}

/* Prevent overlap with mic */
.stChatInputContainer {
    padding-right: 80px !important;
}

/* 🎙️ Mic button at bottom-right */
button[data-testid="baseButton-mic_btn"] {
    position: fixed;
    bottom: 14px;
    right: 20px;
    z-index: 999;

    width: 50px;
    height: 50px;
    border-radius: 50%;

    background-color: #0d6efd;
    color: white;
    font-size: 22px;

    border: none;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
}

/* Hover effect */
button[data-testid="baseButton-mic_btn"]:hover {
    background-color: #0b5ed7;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# 3. Sidebar (Dashboard)
with st.sidebar:
    st.title("🩺 Patient Dashboard")
    st.info("CareBot analyzes your symptoms in real-time to assist with triage.")

    if st.button("🔄 Clear Consultation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("📋 Current Symptoms")

    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        with st.container(border=True):
            summary = summarize_symptoms(st.session_state.messages)
            st.markdown(summary)
    else:
        st.write("No symptoms reported yet.")

# Title and Tag line for page
st.title("CareBot: Rural Healthcare Assistant")
st.caption("AI-Powered Preliminary Diagnostic Support | 2026 Edition")

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    avatar = "🩺" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Input : Text or Voice
prompt = st.chat_input("Tell me how you are feeling...")
mic_clicked = st.button("🎙️", key="mic_btn")

user_query = None
if prompt:
    user_query = prompt
elif mic_clicked:
    with st.spinner("🎙️ Listening..."):
        voice_text = listen_to_user()
        if voice_text:
            user_query = voice_text
        else:
            st.warning("Could not understand audio")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # response logic
    with st.chat_message("assistant", avatar="🩺"):
        response_placeholder = st.empty()
        
        with st.spinner("Analyzing symptoms..."):
            # Call brain.py logic
            response = get_carebot_response(user_query, st.session_state.messages)
        
        full_text = ""
        for word in response.split(" "):
            full_text += word + " "
            time.sleep(0.02)
            response_placeholder.markdown(full_text + "▌")
        
        # Final display without cursor
        response_placeholder.markdown(full_text)
        # Save the finalized response to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_text
        })
    st.rerun()