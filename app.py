import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. THE EXACT UI (Clean Reader Aesthetic) ---
st.set_page_config(page_title="ChickenAI - Clean Reader Edition", layout="wide", initial_sidebar_state="expanded")

# This CSS mimics your screenshot exactly and kills all icons
st.markdown("""
    <style>
    /* Dark Theme Backgrounds */
    .stApp { background-color: #1E1E1E; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #2D2D2D; border-right: 1px solid #444; }
    
    /* Hide the default User/Bot icons completely */
    [data-testid="stChatMessageAvatarUser"], 
    [data-testid="stChatMessageAvatarAssistant"],
    .st-emotion-cache-17l2fup { 
        display: none !important; 
    }

    /* Main Chat Window Styling */
    .chat-window {
        background-color: #262626;
        border: 1px solid #444;
        border-radius: 12px;
        padding: 30px;
        min-height: 65vh;
        margin-bottom: 20px;
    }

    /* Sidebar Buttons (New Chat, Delete) */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; }
    
    /* Input Box at the bottom */
    .stTextInput input { background-color: #333 !important; color: white !important; border: 1px solid #444 !important; }
    
    /* Separator line like in your screenshot */
    .msg-sep { border-bottom: 1px solid #444; margin: 15px 0; opacity: 0.5; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = [datetime.now().strftime("%Y-%m-%d_%H-%M")]

# --- 3. SIDEBAR (Exact Match) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>CHICKEN AI</h1>", unsafe_allow_html=True)
    if st.button("➕ New Chat", type="primary"):
        st.session_state.messages = []
        st.session_state.history.append(datetime.now().strftime("%Y-%m-%d_%H-%M"))
    
    st.write("")
    st.markdown("<div style='background: #333; padding: 5px; text-align: center; border-radius: 5px;'>History</div>", unsafe_allow_html=True)
    for h in st.session_state.history:
        st.button(f"📅 {h}", key=f"hist_{h}")
    
    st.divider()
    if st.button("🗑️ Delete Chat", type="secondary"):
        st.session_state.messages = []
    st.toggle("Voice Mode")

# --- 4. MAIN CHAT AREA ---
with st.container():
    st.markdown('<div class="chat-window">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        label = "USER" if msg["role"] == "user" else "AI"
        st.markdown(f"**{label}:** {msg['content']}")
        st.markdown('<div class="msg-sep"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. INPUT AREA ---
input_col, btn_col = st.columns([9, 1])
with input_col:
    user_input = st.text_input("", placeholder="Type your message here...", label_visibility="collapsed")
with btn_col:
    send_pressed = st.button("Send")

# --- 6. API CALL ---
if (send_pressed or user_input) and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    try:
        # Get the key from your Secrets
        api_key = st.secrets.get("API_KEY")
        
        if not api_key:
            st.error("Error: API_KEY not found in Secrets. Check Advanced Settings.")
        else:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                data=json.dumps({
                    "model": "openai/gpt-4o-mini",
                    "messages": st.session_state.messages
                })
            )
            
            data = response.json()
            
            # This fixes the 'choices' crash by checking the data first
            if "choices" in data:
                ai_reply = data["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.rerun()
            else:
                # If OpenRouter is mad at the key, it will tell you why here
                error_info = data.get("error", {}).get("message", "Invalid API Key")
                st.error(f"AI Connection Error: {error_info}")
                
    except Exception as e:
        st.error(f"System Error: {e}")
