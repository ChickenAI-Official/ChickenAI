import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. THE LOOK (Total Icon Kill) ---
st.set_page_config(page_title="Chicken AI", layout="wide")

st.markdown("""
    <style>
    /* Force Dark Theme */
    .stApp { background-color: #1E1E1E !important; color: white !important; }
    [data-testid="stSidebar"] { background-color: #2D2D2D !important; }
    
    /* The Chat Box from your screenshot */
    .clean-chat-box {
        background-color: #262626;
        border: 1px solid #444;
        border-radius: 10px;
        padding: 20px;
        height: 65vh;
        overflow-y: auto;
        font-family: sans-serif;
    }
    .user-line { color: #FFFFFF; font-weight: bold; margin-top: 10px; }
    .ai-line { color: #00FFCC; font-weight: bold; margin-top: 10px; }
    .sep { border-bottom: 1px solid #444; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# --- 2. STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("CHICKEN AI")
    if st.button("➕ New Chat", type="primary"):
        st.session_state.messages = []
        st.rerun()
    st.write("---")
    st.write("History")
    st.button(datetime.now().strftime("%Y-%m-%d"), disabled=True)

# --- 4. MAIN WINDOW (The exact image look) ---
# We are NOT using st.chat_message here so icons CANNOT appear.
chat_html = '<div class="clean-chat-box">'
for msg in st.session_state.messages:
    if msg["role"] == "user":
        chat_html += f'<div class="user-line">USER: {msg["content"]}</div>'
    else:
        chat_html += f'<div class="ai-line">AI: {msg["content"]}</div>'
    chat_html += '<div class="sep"></div>'
chat_html += '</div>'

st.markdown(chat_html, unsafe_allow_html=True)

# --- 5. INPUT ---
col1, col2 = st.columns([9, 1])
with col1:
    user_input = st.text_input("", placeholder="Type your message here...", label_visibility="collapsed")
with col2:
    send = st.button("Send")

# --- 6. API ---
if (send or user_input) and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    try:
        api_key = st.secrets["API_KEY"]
        r = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            data=json.dumps({
                "model": "openai/gpt-4o-mini",
                "messages": st.session_state.messages
            })
        )
        data = r.json()
        if "choices" in data:
            st.session_state.messages.append({"role": "assistant", "content": data["choices"][0]["message"]["content"]})
            st.rerun()
        else:
            st.error(f"Error: {data.get('error', {}).get('message', 'Check API Key')}")
    except Exception as e:
        st.error(f"System Error: {e}")
