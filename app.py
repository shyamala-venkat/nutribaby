"""NutriBaby — Streamlit entry point."""

import logging

from dotenv import load_dotenv

load_dotenv()

import streamlit as st  # noqa: E402

from src.ui import analysis, home, landing, log_meal  # noqa: E402

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="NutriBaby", page_icon="🍼", layout="centered")

pg = st.navigation(
    [
        st.Page(landing.render, title="Home", icon="🏠", url_path="home"),
        st.Page(home.render, title="Baby Profiles", icon="👶", url_path="babies"),
        st.Page(log_meal.render, title="Log Meal", icon="🍽️", url_path="log-meal"),
        st.Page(analysis.render, title="Analysis", icon="📊", url_path="analysis"),
    ]
)
pg.run()
