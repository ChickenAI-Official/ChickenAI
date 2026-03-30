import streamlit as st
import requests
import json
import os

# --- CONFIG ---
API_KEY = "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"
MODEL = "google/gemini-2.0-flash-001"
SAVE_FOLDER = "saved_chats"

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

st.set_page_config(page_title="Chicken AI", page_icon="🐔", layout="wide")

# --- PRO DARK STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    [data-testid="stSidebar"] { background-color: #0c0c0c !important; border-right: 1px solid #222; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #111; color: white; border: 1px solid #333; }
    .stButton>button:hover { background-color: #222; border-color: #444; }
    /* Fix Chat Bubble look */
    [data-testid="stChatMessage"] { background-color: #0e0e0e !important; border: 1px solid #1a1a1a; border-radius: 12px; }
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = "Guest"
if "messages" not in st.session_state: st.session_state.messages = []
if "current_file" not in st.session_state: st.session_state.current_file = None

# --- SIGN UP / LOGIN PAGE ---
if not st.session_state.auth:
    st.markdown("<br><br><h1 style='text-align: center;'>🐔 Chicken AI</h1>", unsafe_allow_html=True)
    with st.container():
        _, center, _ = st.columns([1, 1, 1])
        with center:
            name_input = st.text_input("Name", placeholder="Enter your name")
            if st.button("🚀 Enter Coop"):
                st.session_state.user = name_input if name_input else "Guest"
                st.session_state.auth = True
                st.rerun()

# --- MAIN APP WITH MENU ---
else:
    # SIDEBAR MENU
    with st.sidebar:
        st.title("🐔 History")
        if st.button("➕ New Chat"):
            st.session_state.messages = []
            st.session_state.current_file = None
            st.rerun()
        
        st.write("---")
        files = [f for f in os.listdir(SAVE_FOLDER) if f.endswith(".json")]
        for f in sorted(files, reverse=True):
            display_name = f.replace(".json", "").replace("_", " ")
            if st.button(f"📄 {display_name}", key=f):
                with open(os.path.join(SAVE_FOLDER, f), "r") as chat_file:
                    st.session_state.messages = json.load(chat_file)
                    st.session_state.current_file = f
                st.rerun()
        
        st.write("---")
        if st.sidebar.button("🚪 Logout"):
            st.session_state.auth = False
            st.rerun()

    # MAIN CHAT AREA
    st.title(f"Welcome, {st.session_state.user}")
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Message Chicken AI..."):
        # Auto-name file based on first message
        if not st.session_state.current_file:
            clean_name = "".join(x for x in prompt[:15] if x.isalnum() or x==" ")
            st.session_state.current_file = f"{clean_name.strip().replace(' ', '_')}.json"

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"model": MODEL, "messages": st.session_state.messages}
            )
            output = r.json()['choices'][0]['message']['content']
            st.markdown(output)
            st.session_state.messages.append({"role": "assistant", "content": output})
            
            # SAVE CHAT
            with open(os.path.join(SAVE_FOLDER, st.session_state.current_file), "w") as f:
                json.dump(st.session_state.messages, f)