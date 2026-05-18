"""NutriBaby landing / home page."""

import streamlit as st

from src.ui.styles import inject


def render() -> None:
    inject()

    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="nb-hero">
        <div class="nb-hero-icon">🍼</div>
        <h1>NutriBaby</h1>
        <div class="tagline">Know what your baby needs, every bite of the way.</div>
        <div class="subtitle">
            Log meals in plain language. Get age-appropriate nutrition insights
            backed by real USDA data — in seconds.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<p style='text-align:center; color:#78716C; font-size:0.85rem;'>"
        "👈 Use the sidebar to navigate</p>",
        unsafe_allow_html=True,
    )

    # ── Feature cards ────────────────────────────────────────────────────────
    st.markdown(
        "<div class='nb-section-label' style='text-align:center; margin-bottom:1rem;'>"
        "What NutriBaby does</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="nb-feature">
            <div class="icon">🗣️</div>
            <h3>Natural Language Logging</h3>
            <p>Type "half a banana and some oatmeal" — NutriBaby understands, no dropdowns needed.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="nb-feature">
            <div class="icon">🥕</div>
            <h3>Real Nutrition Data</h3>
            <p>Backed by the USDA FoodData Central database. AI fallback for home-cooked and ethnic foods.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="nb-feature">
            <div class="icon">📊</div>
            <h3>Age-Matched Targets</h3>
            <p>Daily RDA targets adjust automatically as your baby grows from 0 to 36 months.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── How it works ─────────────────────────────────────────────────────────
    col_steps, col_safety = st.columns([3, 2], gap="large")

    with col_steps:
        st.markdown(
            "<div class='nb-section-label'>How it works</div>",
            unsafe_allow_html=True,
        )
        st.markdown("""
        <div class="nb-step">
            <div class="num">1</div>
            <div>
                <h4>Create your baby's profile</h4>
                <p>Enter name, date of birth, known allergies, and diet type.</p>
            </div>
        </div>
        <div class="nb-step">
            <div class="num">2</div>
            <div>
                <h4>Log what they ate, in your own words</h4>
                <p>Claude extracts each food item and looks up its nutrition automatically.</p>
            </div>
        </div>
        <div class="nb-step">
            <div class="num">3</div>
            <div>
                <h4>See today's nutrition at a glance</h4>
                <p>Progress bars show how close you are to each daily nutrient target.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_safety:
        st.markdown(
            "<div class='nb-section-label'>Built-in safety</div>",
            unsafe_allow_html=True,
        )
        st.markdown("""
        <div class="nb-safety">
            <h3>🛡️ Hard-coded safety checks</h3>
            <div class="nb-safety-item">🍯 Honey blocked for babies under 12 months</div>
            <div class="nb-safety-item">🥜 Whole nut warnings for under 4 years</div>
            <div class="nb-safety-item">⚠️ Every suggestion cross-checked against your baby's allergy list</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Disclaimer ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="nb-disclaimer">
        ⚠️ <strong>This is a learning project.</strong>
        NutriBaby is built to explore AI-assisted nutrition tracking — it is
        <strong>not a substitute for medical advice</strong>. Nutrition values are estimates.
        Always consult your pediatrician before making changes to your baby's diet.
    </div>
    """, unsafe_allow_html=True)
