import streamlit as st
import requests
import json
from datetime import datetime

# --- 1. PAGE SETUP & EXACT THEME ---
st.set_page_config(page_title="ChickenAI", layout="wide")

# CSS to match your screenshot 1:1 and kill all icons
st.markdown("""
    <style>
    /* Dark Backgrounds */
    .stApp { background-color: #1E1E1E !important; color: white !important; }
    [data-testid="stSidebar"] { background-color: #2D2D2D !important; border-right: 1px solid #444; }
    
    /* Kill all default Streamlit Icons/Avatars */
    [data-testid="stChatMessageAvatarUser"], 
    [data-testid="stChatMessageAvatarAssistant"],
    .st-emotion-cache-17l2fup { 
        display: none !important; 
    }

    /* The Main Chat Window (The big dark box) */
    .chat-container {
        background-color: #262626;
        border: 1px solid #444;
        border-radius: 12px;
        padding: 25px;
        height: 60vh;
        overflow-y: auto;
        margin-bottom: 20px;
    }

    /* Make Sidebar Text White and Visible */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: white !important;
    }
    
    /* Style the buttons to match the image */
    .stButton>button { width: 100%; border-radius: 8px; }
    
    /* Input box styling */
    .stTextInput input { background-color: #333 !important; color: white !important; border: 1px solid #444 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = [datetime.now().strftime("%Y-%m-%d_%H-%M")]

# --- 3. SIDEBAR (Exactly like the goal image) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>CHICKEN AI</h1>", unsafe_allow_html=True)
    if st.button("➕ New Chat", type="primary"):
        st.session_state.messages = []
        st.session_state.history.append(datetime.now().strftime("%Y-%m-%d_%H-%M"))
    
    st.write("---")
    st.markdown("<div style='background:#333; padding:5px; border-radius:5px; text-align:center;'>History</div>", unsafe_allow_html=True)
    for h in st.session_state.history:
        st.button(f"📅 {h}", key=f"h_{h}")
    
    st.write("---")
    if st.button("🗑️ Delete Chat", type="secondary"):
        st.session_state.messages = []
    st.toggle("Voice Mode")

# --- 4. THE CHAT BOX ---
# This creates the clean black box from your screenshot
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    label = "USER" if msg["role"] == "user" else "AI"
    st.markdown(f"**{label}:** {msg['content']}")
    st.markdown("<hr style='border-top: 1px solid #333;'>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. INPUT AREA ---
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
            # Fixes the 'choices' error by showing the actual message
            err = result.get("error", {}).get("message", "Check your API Key")
            st.error(f"Error: {err}")
            
    except Exception as e:
        st.error(f"System Error: {e}")
