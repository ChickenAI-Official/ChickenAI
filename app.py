import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. LAYOUT & STYLE (Matching your Screenshot) ---
st.set_page_config(page_title="ChickenAI - Clean Reader Edition", layout="wide", initial_sidebar_state="expanded")

# This CSS kills the default icons and fixes the "Hot Ass" alignment
st.markdown("""
    <style>
    /* Dark Theme Backgrounds */
    .stApp { background-color: #1E1E1E; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #2D2D2D; border-right: 1px solid #444; }
    
    /* The Main Chat Container */
    .chat-window {
        background-color: #262626;
        border: 1px solid #444;
        border-radius: 12px;
        padding: 25px;
        height: 65vh;
        overflow-y: auto;
        margin-bottom: 20px;
        font-family: 'Inter', sans-serif;
    }

    /* Removing default Streamlit Padding */
    .block-container { padding-top: 2rem; }
    
    /* Sidebar Buttons */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; }
    
    /* Clean Text spacing */
    .message-line { margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIC & STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = [datetime.now().strftime("%Y-%m-%d_%H-%M")]

# --- 3. SIDEBAR (Exactly like the image) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>CHICKEN AI</h1>", unsafe_allow_html=True)
    if st.button("➕ New Chat", type="primary"):
        st.session_state.messages = []
        st.session_state.history.append(datetime.now().strftime("%Y-%m-%d_%H-%M"))
    
    st.write("---")
    st.caption("History")
    for h in st.session_state.history:
        st.button(f"📅 {h}", key=f"hist_{h}")
    
    st.write("---")
    if st.button("🗑️ Delete Chat", type="secondary"):
        st.session_state.messages = []
    st.toggle("Voice Mode")

# --- 4. THE CHAT WINDOW ---
# No icons here—just clean USER/AI labels as requested
chat_placeholder = st.empty()
with chat_placeholder.container():
    st.markdown('<div class="chat-window">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        label = "USER" if msg["role"] == "user" else "AI"
        st.markdown(f"**{label}:** {msg['content']}")
        st.markdown('<div class="message-line"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. INPUT BAR (Bottom) ---
col1, col2 = st.columns([9, 1])
with col1:
    user_input = st.text_input("", placeholder="Type your message here...", label_visibility="collapsed")
with col2:
    send_btn = st.button("Send")

# --- 6. AI CONNECTION ---
if (send_btn or user_input) and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
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
        
        result = response.json()
        
        if "choices" in result:
            answer = result['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
        else:
            err = result.get("error", {}).get("message", "API Error")
            st.error(f"Error: {err}")
            
    except Exception as e:
        st.error(f"System Error: {e}")
