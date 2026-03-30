import streamlit as st
import requests
import json

# --- THE CLEAN LOOK ---
st.set_page_config(page_title="Chicken AI Desktop", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #1E1E1E; color: white; }
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { display: none !important; }
    .stChatMessage { background-color: #262626 !important; border: 1px solid #444 !important; }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("CHICKEN AI (DESKTOP)")

# --- DISPLAY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(f"**{'USER' if msg['role'] == 'user' else 'AI'}:** {msg['content']}")

# --- INPUT & LOGIC ---
if prompt := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(f"**USER:** {prompt}")

    # DIRECT API CALL
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": st.session_state.messages
    }
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
    else:
        st.error(f"Error: {response.text}")
