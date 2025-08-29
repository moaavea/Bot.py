import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from groq import Groq
import streamlit as st

# ---------------- Load API Key ----------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("⚠️ API key not found. Please add GROQ_API_KEY to your .env file.")
    st.stop()

# Initialize client
client = Groq(api_key=groq_api_key)

# ---------------- Page Config ----------------
st.set_page_config(page_title="CareerCraft AI", page_icon="💼", layout="wide")

# ---------------- Title ----------------
st.title("💼 CareerCraft AI - Career Mentor")

# ---------------- Sidebar (All Options) ----------------
with st.sidebar:
    st.header("⚙️ Settings")

    model = st.selectbox("🤖 Model", ["llama-3.3-70b-versatile","openai/gpt-oss-120b","qwen/qwen3-32b"])
    temperature = st.slider("🌡️ Temperature", 0.0, 1.0, 0.5)
    max_tokens = st.slider("🔢 Max Tokens", 20,100,300, step=50)  # FIXED RANGE

    if st.button("🌙 Toggle Dark Mode", key="dark_mode"):
        st.session_state["dark_mode"] = not st.session_state.get("dark_mode", False)

    st.subheader("📄 Upload Resume")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        st.success("✅ Resume uploaded and processed!")

    if st.button("🧹 Clear Chat", key="clear_chat"):
        st.session_state.history = []
        st.rerun()

# ---------------- Chat Section (Center) ----------------
st.subheader("💬 Chat with Career Mentor AI")

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Show chat messages
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"<div style='text-align: right; color: blue;'>🧑‍💻 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align: left; color: green;'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

# User input (ONLY thing outside sidebar)
user_input = st.text_input("✍️ Type your message here...")

# ---- Send button ----
if st.button("Send", use_container_width=True, key="send_btn"):
    if user_input.strip():
        # Store user message
        st.session_state.history.append({"role": "user", "content": user_input})

        # ---- Call Groq API ----
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful career mentor AI."},
                {"role": "user", "content": user_input},
            ],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        bot_reply = chat_completion.choices[0].message.content

        # Store bot reply
        st.session_state.history.append({"role": "bot", "content": bot_reply})
        st.rerun()
