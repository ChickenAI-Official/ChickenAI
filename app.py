import streamlit as st
import requests
import json
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="ChickenAI - Clean Reader Edition", layout="wide")

# --- STYLE (The sleek dark UI) ---
st.markdown("""
    <style>
    .stApp { background-color: #1E1E1E; color: white; }
    [data-testid="stSidebar"] { background-color: #2D2D2D; border-right: 1px solid #444; }
    .chat-container {
        background-color: #262626;
        border: 1px solid #444;
        border-radius: 10px;
        padding: 20px;
        min-height: 400px;
        margin-bottom: 20px;
    }
    .stButton>button { width: 100%; border-radius: 5px; }
    .delete-btn>button { background-color: #FF4B4B; color: white; }
    .send-btn>button { background-color: #00C897; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = [datetime.now().strftime("%Y-%m-%d_%H-%M")]

# --- SIDEBAR ---
with st.sidebar:
    st.header("CHICKEN AI")
    if st.button("➕ New Chat", type="primary"):
        st.session_state.messages = []
        st.session_state.history.append(datetime.now().strftime("%Y-%m-%d_%H-%M"))
    
    st.write("---")
    st.subheader("History")
    for h in st.session_state.history:
        st.button(f"📅 {h}", key=h)
    
    st.write("---")
    if st.button("🗑️ Delete Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = []
    st.toggle("Voice Mode")

# --- MAIN CHAT AREA ---
container = st.container()
with container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role_label = "USER" if msg["role"] == "user" else "AI"
        st.write(f"**{role_label}:** {msg['content']}")
        st.write("---")
    st.markdown('</div>', unsafe_allow_html=True)

# --- INPUT AREA ---
col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.text_input("", placeholder="Type your message here...", label_visibility="collapsed")
with col2:
    send_clicked = st.button("Send")

if (send_clicked or user_input) and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Call AI
    try:
        api_key = st.secrets["API_KEY"]
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            data=json.dumps({
                "model": "openai/gpt-4o-mini",
                "messages": st.session_state.messages
            })
        )
        
        data = response.json()
        
        # Check if the AI actually replied
        if "choices" in data:
            ai_reply = data["choices"][0]["message"]["content"]
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.rerun()
        else:
            # Show the actual error from the AI provider
            error_msg = data.get("error", {}).get("message", "Connection failed")
            st.error(f"AI Brain Error: {error_msg}")
            
    except Exception as e:
        st.error(f"System Error: {e}")
