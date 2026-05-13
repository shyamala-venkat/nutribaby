"""NutriBaby — Streamlit entry point."""

import logging

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # must run before any src imports that use the client

from src.llm.client import chat  # noqa: E402
from src.llm.prompts import HELLO_WORLD_SYSTEM  # noqa: E402

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="NutriBaby", page_icon="🍼", layout="centered")

st.title("🍼 NutriBaby")
st.caption("Learning project — not medical advice. Consult your pediatrician.")
st.divider()

st.subheader("Claude connection test")
user_input = st.text_input(
    "Ask NutriBaby anything:",
    placeholder="e.g. What foods are good for a 9-month-old?",
)

if st.button("Send", disabled=not user_input):
    with st.spinner("Thinking…"):
        try:
            reply = chat(
                messages=[{"role": "user", "content": user_input}],
                system=HELLO_WORLD_SYSTEM,
            )
            st.success(reply)
        except Exception as e:
            st.error(f"Error: {e}")
