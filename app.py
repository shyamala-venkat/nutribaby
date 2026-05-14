"""NutriBaby — Streamlit entry point."""

import logging

from dotenv import load_dotenv

load_dotenv()

import streamlit as st  # noqa: E402

from src.ui import analysis, home, log_meal  # noqa: E402

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="NutriBaby", page_icon="🍼", layout="centered")

pg = st.navigation(
    [
        st.Page(home.render, title="Baby Profiles", icon="👶"),
        st.Page(log_meal.render, title="Log Meal", icon="🍽️"),
        st.Page(analysis.render, title="Analysis", icon="📊"),
    ]
)
pg.run()
