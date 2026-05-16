"""Nutrition analysis page — daily RDA progress dashboard."""

from datetime import date

import streamlit as st

from src.db.queries import get_all_babies, get_todays_food_items
from src.nutrition.rda import compute_daily_progress, get_rda_label


def render() -> None:
    st.header("📊 Nutrition Analysis")
    st.caption(
        "Values are estimates based on per-100g data and approximate serving sizes. "
        "Not medical advice — consult your pediatrician."
    )

    babies = get_all_babies()
    if not babies:
        st.warning("No baby profiles yet. Create one on the Baby Profiles page.")
        return

    baby_options = {b.name: b for b in babies}
    selected_name = st.selectbox("Baby", options=list(baby_options.keys()))
    baby = baby_options[selected_name]

    rda_label = get_rda_label(baby.age_months)
    st.markdown(
        f"**Age:** {baby.age_display} &nbsp;·&nbsp; "
        f"**RDA band:** {rda_label} &nbsp;·&nbsp; "
        f"**Date:** {date.today().strftime('%B %d, %Y')}"
    )
    st.divider()

    food_rows = get_todays_food_items(baby.id)  # type: ignore[arg-type]

    if not food_rows:
        st.info("No meals logged today. Head to **Log Meal** to add one.")
        return

    progress = compute_daily_progress(food_rows, baby.age_months)

    # ── Nutrient progress bars ────────────────────────────────────────────────
    st.subheader("Today's progress vs daily RDA")

    for nutrient, data in progress.items():
        pct: float = data["pct"]
        actual: float = data["actual"]
        target: float = data["target"]
        label: str = data["label"]

        icon = "🟢" if pct >= 0.8 else ("🟡" if pct >= 0.5 else "🔴")
        pct_display = min(int(pct * 100), 200)

        col_label, col_bar, col_value = st.columns([2, 4, 2])
        with col_label:
            st.markdown(f"{icon} **{label}**")
        with col_bar:
            st.progress(min(pct, 1.0))
        with col_value:
            st.markdown(f"`{actual:.1f}` / `{target}` &nbsp;*({pct_display}%)*")

    # ── Summary metrics ───────────────────────────────────────────────────────
    st.divider()
    on_track = sum(1 for d in progress.values() if d["pct"] >= 0.8)
    low = sum(1 for d in progress.values() if d["pct"] < 0.5)

    c1, c2, c3 = st.columns(3)
    c1.metric("On track (≥ 80%)", f"{on_track} / {len(progress)}")
    c2.metric("Low (< 50%)", low)
    c3.metric("Foods logged today", len(food_rows))

    # ── Today's food list ─────────────────────────────────────────────────────
    st.divider()
    st.subheader("Today's food log")
    st.dataframe(
        [
            {
                "Food": r["food_name"],
                "Qty": f"{r['quantity']} {r['unit']}",
                "Meal": r["meal_type"],
                "Cal/100g": f"{r['calories_kcal']:.0f}" if r["calories_kcal"] else "—",
                "Prot/100g": f"{r['protein_g']:.1f}g" if r["protein_g"] else "—",
                "Source": r["source"] or "—",
            }
            for r in food_rows
        ],
        use_container_width=True,
        hide_index=True,
    )
