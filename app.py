import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. THE LOOK (Strict Clean Reader Aesthetic) ---
st.set_page_config(page_title="ChickenAI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Force Dark Theme */
    .stApp { background-color: #1E1E1E; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #2D2D2D; border-right: 1px solid #444; }
    
    /* Remove all default Streamlit user/assistant icons */
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    
    /* Main Chat Container */
    .chat-box {
        background-color: #262626;
        border: 1px solid #444;
        border-radius: 12px;
        padding: 30px;
        height: 70vh;
        overflow-y: auto;
        margin-bottom: 20px;
    }

    /* Sidebar buttons */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .message-sep { border-bottom: 1px solid #333; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = [datetime.now().strftime("%Y-%m-%d_%H:%M")]

# --- 3. SIDEBAR (Exactly like your image) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>CHICKEN AI</h1>", unsafe_allow_html=True)
    if st.button("➕ New Chat", type="primary"):
        st.session_state.messages = []
        st.session_state.history.append(datetime.now().strftime("%Y-%m-%d_%H-%M"))
    
    st.write("---")
    st.caption("History")
    for h in st.session_state.history:
        st.button(f"📅 {h}", key=f"h_{h}")
    
    st.write("---")
    if st.button("🗑️ Delete Chat", type="secondary"):
        st.session_state.messages = []
    st.toggle("Voice Mode")

# --- 4. CHAT WINDOW ---
with st.container():
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role = "USER" if msg["role"] == "user" else "AI"
        st.markdown(f"**{role}:** {msg['content']}")
        st.markdown('<div class="message-sep"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. INPUT BAR ---
col1, col2 = st.columns([9, 1])
with col1:
    user_input = st.text_input("", placeholder="Type your message here...", label_visibility="collapsed")
with col2:
    send = st.button("Send")

# --- 6. AI CONNECTION ---
if (send or user_input) and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    try:
        # Check if secret exists
        if "API_KEY" not in st.secrets:
            st.error("Error: API_KEY missing in Streamlit Secrets!")
        else:
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
                # This catches the 'User not found' error
                error_msg = result.get("error", {}).get("message", "Check API Key")
                st.error(f"AI Brain Error: {error_msg}")
            
    except Exception as e:
        st.error(f"System Error: {e}")
