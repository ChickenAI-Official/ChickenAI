import streamlit as st
import requests
import json

# --- 1. THE LOOK (Professional Dark Mode) ---
st.set_page_config(page_title="Chicken AI", page_icon="🐔", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1 { color: #FFFFFF; font-family: 'Inter', sans-serif; text-align: center; }
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; }
    </style>
    <h1>CHICKEN <span style="color:#FF4B4B;">AI</span></h1>
""", unsafe_allow_html=True)

# --- 2. THE BRAIN (Session State) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. THE SIDEBAR ---
with st.sidebar:
    st.title("Settings")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    st.info("Version 5.4 - Powered by OpenRouter")

# --- 4. DISPLAY CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. CHAT INPUT & API CALL ---
if prompt := st.chat_input("What's on your mind?"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call AI
    try:
        api_key = st.secrets["API_KEY"]
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            data=json.dumps({
                "model": "openai/gpt-4o-mini", # The reliable workhorse
                "messages": st.session_state.messages
            })
        )
        
        data = response.json()
        
        # Check if AI responded correctly
        if "choices" in data:
            full_response = data["choices"][0]["message"]["content"]
            with st.chat_message("assistant"):
                st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            # If the API key is wrong, it will show the error here
            error_text = data.get("error", {}).get("message", "Unknown Error")
            st.error(f"AI Connection Error: {error_text}")

    except Exception as e:
        st.error(f"System Error: {e}")
