"""Global CSS design system for NutriBaby. Call inject() once in app.py."""

import streamlit as st

# ── Color tokens ─────────────────────────────────────────────────────────────
PRIMARY = "#F97316"
PRIMARY_HOVER = "#EA580C"
PRIMARY_LIGHT = "#FDBA74"
PRIMARY_BG = "#FFF7ED"
PRIMARY_BORDER = "#FED7AA"
TEXT_DARK = "#1C1917"
TEXT_MID = "#78716C"
SUCCESS = "#16A34A"
SUCCESS_BG = "#F0FDF4"
SUCCESS_BORDER = "#BBF7D0"
WARNING_COLOR = "#D97706"
WARNING_BG = "#FFFBEB"
WARNING_BORDER = "#FDE68A"
DANGER = "#DC2626"
DANGER_BG = "#FEF2F2"
DANGER_BORDER = "#FECACA"

_CSS = f"""
<style>
/* ── Base ──────────────────────────────────────────── */
.stApp {{
    background-color: #FFFBF7;
}}
section[data-testid="stSidebar"] {{
    background-color: {PRIMARY_BG};
    border-right: 2px solid {PRIMARY_BORDER};
}}

/* ── Buttons ───────────────────────────────────────── */
.stButton > button[kind="primary"] {{
    background-color: {PRIMARY};
    border: none;
    color: white;
    border-radius: 8px;
    font-weight: 600;
    transition: background-color 0.2s;
}}
.stButton > button[kind="primary"]:hover {{
    background-color: {PRIMARY_HOVER};
    border: none;
    color: white;
}}
.stButton > button {{
    border-radius: 8px;
    border: 1px solid {PRIMARY_BORDER};
    color: {TEXT_DARK};
}}

/* ── Progress bars ─────────────────────────────────── */
.stProgress > div > div > div > div {{
    background-color: {PRIMARY};
}}

/* ── Metrics ───────────────────────────────────────── */
[data-testid="stMetric"] {{
    background: white;
    border: 1px solid {PRIMARY_BORDER};
    border-radius: 10px;
    padding: 0.75rem 1rem;
}}
[data-testid="stMetricLabel"] {{
    color: {TEXT_MID} !important;
    font-size: 0.8rem !important;
}}
[data-testid="stMetricValue"] {{
    color: {TEXT_DARK} !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}}

/* ── Dividers ──────────────────────────────────────── */
hr {{ border-color: {PRIMARY_BORDER}; }}

/* ── Hero ──────────────────────────────────────────── */
.nb-hero {{
    background: linear-gradient(135deg, {PRIMARY_BG} 0%, #FFEDD5 100%);
    border-radius: 16px;
    padding: 3rem 2rem 2.5rem;
    text-align: center;
    border: 1px solid {PRIMARY_BORDER};
    margin-bottom: 2rem;
}}
.nb-hero-icon {{
    font-size: 3.5rem;
    line-height: 1;
    margin-bottom: 0.5rem;
}}
.nb-hero h1 {{
    color: {TEXT_DARK};
    font-size: 2.4rem;
    font-weight: 800;
    margin: 0 0 0.4rem 0;
}}
.nb-hero .tagline {{
    color: {PRIMARY};
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 0.6rem;
}}
.nb-hero .subtitle {{
    color: {TEXT_MID};
    font-size: 0.95rem;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}}

/* ── Feature cards ─────────────────────────────────── */
.nb-feature {{
    background: white;
    border-radius: 12px;
    padding: 1.5rem 1.25rem;
    text-align: center;
    border: 1px solid {PRIMARY_BORDER};
    height: 100%;
    box-shadow: 0 1px 4px rgba(249,115,22,0.07);
}}
.nb-feature .icon {{
    font-size: 2.2rem;
    margin-bottom: 0.75rem;
}}
.nb-feature h3 {{
    color: {TEXT_DARK};
    font-size: 0.95rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
}}
.nb-feature p {{
    color: {TEXT_MID};
    font-size: 0.825rem;
    margin: 0;
    line-height: 1.5;
}}

/* ── How-it-works steps ────────────────────────────── */
.nb-step {{
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem 1.25rem;
    background: white;
    border-radius: 10px;
    border-left: 4px solid {PRIMARY};
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
.nb-step .num {{
    background: {PRIMARY};
    color: white;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.875rem;
    flex-shrink: 0;
    margin-top: 1px;
}}
.nb-step h4 {{
    margin: 0 0 0.2rem 0;
    color: {TEXT_DARK};
    font-size: 0.9rem;
    font-weight: 700;
}}
.nb-step p {{
    margin: 0;
    color: {TEXT_MID};
    font-size: 0.825rem;
    line-height: 1.5;
}}

/* ── General cards ─────────────────────────────────── */
.nb-card {{
    background: white;
    border: 1px solid {PRIMARY_BORDER};
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}

/* ── Section label ─────────────────────────────────── */
.nb-section-label {{
    color: {PRIMARY};
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.1rem;
}}

/* ── Food item row ─────────────────────────────────── */
.nb-food-row {{
    background: white;
    border: 1px solid {PRIMARY_BORDER};
    border-radius: 10px;
    padding: 0.875rem 1.25rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}}
.nb-food-name {{
    font-weight: 600;
    color: {TEXT_DARK};
    font-size: 0.95rem;
}}
.nb-food-meta {{
    color: {TEXT_MID};
    font-size: 0.8rem;
    margin-top: 0.15rem;
}}

/* ── Badges ────────────────────────────────────────── */
.nb-badge {{
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
}}
.nb-badge-orange {{
    background: {PRIMARY_BG};
    color: {PRIMARY};
    border: 1px solid {PRIMARY_BORDER};
}}
.nb-badge-green {{
    background: {SUCCESS_BG};
    color: {SUCCESS};
    border: 1px solid {SUCCESS_BORDER};
}}
.nb-badge-red {{
    background: {DANGER_BG};
    color: {DANGER};
    border: 1px solid {DANGER_BORDER};
}}

/* ── Disclaimer ────────────────────────────────────── */
.nb-disclaimer {{
    background: {PRIMARY_BG};
    border: 1px solid {PRIMARY_BORDER};
    border-radius: 8px;
    padding: 0.875rem 1.25rem;
    font-size: 0.8rem;
    color: {TEXT_MID};
    line-height: 1.5;
}}

/* ── Safety block ──────────────────────────────────── */
.nb-safety {{
    background: white;
    border: 1px solid {PRIMARY_BORDER};
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
}}
.nb-safety h3 {{
    color: {TEXT_DARK};
    font-size: 0.95rem;
    font-weight: 700;
    margin: 0 0 0.75rem 0;
}}
.nb-safety-item {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    color: {TEXT_MID};
    font-size: 0.85rem;
    margin-bottom: 0.4rem;
}}
</style>
"""


def inject() -> None:
    """Inject the global CSS into the current Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)
