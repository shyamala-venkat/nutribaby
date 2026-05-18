"""Nutrition analysis page — daily RDA progress dashboard."""

from datetime import date

import streamlit as st

from src.db.queries import get_all_babies, get_todays_food_items
from src.nutrition.rda import compute_daily_progress, get_rda_label
from src.ui.styles import DANGER, SUCCESS, WARNING_COLOR, inject

# Nutrient icons for the dashboard
_NUTRIENT_ICONS: dict[str, str] = {
    "calories_kcal": "🔥",
    "protein_g": "💪",
    "iron_mg": "🩸",
    "calcium_mg": "🦴",
    "zinc_mg": "⚡",
    "vitamin_d_mcg": "☀️",
    "vitamin_c_mg": "🍊",
}


def render() -> None:
    inject()

    st.markdown(
        "<div class='nb-section-label'>Daily nutrition</div>", unsafe_allow_html=True
    )
    st.markdown("## 📊 Nutrition Analysis")
    st.markdown(
        "<div class='nb-disclaimer' style='margin-bottom:1.5rem;'>"
        "⚠️ Values are estimates based on per-100g data and approximate serving sizes. "
        "Not medical advice — consult your pediatrician."
        "</div>",
        unsafe_allow_html=True,
    )

    babies = get_all_babies()
    if not babies:
        st.markdown("""
        <div class="nb-card" style="text-align:center;padding:2rem;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">👶</div>
            <div style="color:#78716C;">No baby profiles yet. Create one on Baby Profiles.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    baby_options = {b.name: b for b in babies}
    selected_name = st.selectbox("Baby", options=list(baby_options.keys()))
    baby = baby_options[selected_name]

    rda_label = get_rda_label(baby.age_months)
    col1, col2, col3 = st.columns(3)
    col1.metric("Age", baby.age_display)
    col2.metric("RDA Band", rda_label)
    col3.metric("Date", date.today().strftime("%b %d, %Y"))

    st.divider()

    food_rows = get_todays_food_items(baby.id)  # type: ignore[arg-type]

    if not food_rows:
        st.markdown("""
        <div class="nb-card" style="text-align:center;padding:2rem;">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">🍽️</div>
            <div style="color:#78716C;">
                No meals logged today.<br>Head to <strong>Log Meal</strong> to add one.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    progress = compute_daily_progress(food_rows, baby.age_months)

    # ── Summary bar ──────────────────────────────────────────────────────────
    on_track = sum(1 for d in progress.values() if d["pct"] >= 0.8)
    low = sum(1 for d in progress.values() if d["pct"] < 0.5)
    total = len(progress)

    c1, c2, c3 = st.columns(3)
    c1.metric("On track (≥ 80% RDA)", f"{on_track} / {total}", delta=None)
    c2.metric("Needs attention (< 50%)", str(low), delta=None)
    c3.metric("Foods logged today", len(food_rows), delta=None)

    # ── Progress bars ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='nb-section-label'>Nutrients vs daily RDA</div>",
        unsafe_allow_html=True,
    )

    for nutrient, data in progress.items():
        pct: float = data["pct"]
        actual: float = data["actual"]
        target: float = data["target"]
        label: str = data["label"]
        icon = _NUTRIENT_ICONS.get(nutrient, "●")

        if pct >= 0.8:
            color = SUCCESS
            status = "On track"
        elif pct >= 0.5:
            color = WARNING_COLOR
            status = "Getting there"
        else:
            color = DANGER
            status = "Needs attention"

        pct_int = min(int(pct * 100), 200)

        st.markdown(
            f"""<div class="nb-card" style="padding:1rem 1.25rem;margin-bottom:0.6rem;">
                <div style="display:flex;justify-content:space-between;
                    align-items:center;margin-bottom:0.5rem;">
                    <div style="font-weight:600;color:#1C1917;font-size:0.9rem;">
                        {icon} {label}
                    </div>
                    <div style="display:flex;align-items:center;gap:0.75rem;">
                        <span style="font-size:0.8rem;color:#78716C;">
                            {actual:.1f} / {target}
                        </span>
                        <span style="font-size:0.72rem;font-weight:700;
                            color:{color};">{pct_int}%</span>
                    </div>
                </div>
                <div style="background:#F5F5F4;border-radius:4px;height:8px;overflow:hidden;">
                    <div style="background:{color};width:{min(pct_int, 100)}%;
                        height:100%;border-radius:4px;
                        transition:width 0.3s ease;"></div>
                </div>
                <div style="font-size:0.72rem;color:{color};
                    margin-top:0.3rem;">{status}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # ── Food log table ────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        "<div class='nb-section-label'>Today's food log</div>", unsafe_allow_html=True
    )
    st.dataframe(
        [
            {
                "Food": r["food_name"],
                "Qty": f"{r['quantity']} {r['unit']}",
                "Meal": f"{r['meal_type'].capitalize()}",
                "Cal/100g": f"{r['calories_kcal']:.0f}" if r["calories_kcal"] else "—",
                "Prot/100g": f"{r['protein_g']:.1f}g" if r["protein_g"] else "—",
                "Source": r["source"] or "—",
            }
            for r in food_rows
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        "<div class='nb-disclaimer'>"
        "💡 <strong>Tip:</strong> Calories and protein shown are per 100g. "
        "The progress bars above account for actual serving size."
        "</div>",
        unsafe_allow_html=True,
    )
