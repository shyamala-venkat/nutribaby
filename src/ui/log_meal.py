"""Log meal page — text → extract → safety check → confirm → save."""

import streamlit as st

from src.db.models import FoodItem, Meal
from src.db.queries import get_all_babies, get_todays_food_items, save_meal
from src.llm.extractors import extract_meal
from src.nutrition.lookup import lookup_nutrition
from src.safety.rules import check_food_safety, is_blocked
from src.ui.styles import PRIMARY, inject

MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]
MEAL_ICONS = {"breakfast": "🌅", "lunch": "☀️", "dinner": "🌙", "snack": "🍎"}

_KEY_ITEMS = "log_items"
_KEY_WARNINGS = "log_warnings"
_KEY_RAW = "log_raw_input"
_KEY_TYPE = "log_meal_type"


def _clear_extraction() -> None:
    for key in (_KEY_ITEMS, _KEY_WARNINGS, _KEY_RAW, _KEY_TYPE):
        st.session_state.pop(key, None)


def _step_indicator(active: int) -> None:
    """Render a simple 3-step progress indicator."""
    steps = ["Describe", "Review", "Done"]
    cols = st.columns(len(steps))
    for i, (col, label) in enumerate(zip(cols, steps), start=1):
        with col:
            if i < active:
                color = "#16A34A"
                icon = "✓"
            elif i == active:
                color = PRIMARY
                icon = str(i)
            else:
                color = "#D4D4D4"
                icon = str(i)
            st.markdown(
                f"""<div style='text-align:center;'>
                    <div style='width:32px;height:32px;border-radius:50%;
                        background:{color};color:white;font-weight:700;
                        font-size:0.85rem;display:inline-flex;
                        align-items:center;justify-content:center;
                        margin-bottom:0.3rem;'>{icon}</div>
                    <div style='font-size:0.75rem;color:{"#1C1917" if i==active else "#78716C"};
                        font-weight:{"700" if i==active else "400"};'>{label}</div>
                </div>""",
                unsafe_allow_html=True,
            )


def render() -> None:
    inject()

    st.markdown(
        "<div class='nb-section-label'>Track nutrition</div>", unsafe_allow_html=True
    )
    st.markdown("## 🍽️ Log a Meal")

    babies = get_all_babies()
    if not babies:
        st.markdown("""
        <div class="nb-card" style="text-align:center;padding:2rem;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">👶</div>
            <div style="color:#78716C;">
                No baby profiles found.<br>
                Create one on the <strong>Baby Profiles</strong> page first.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Selectors ─────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        baby_options = {b.name: b for b in babies}
        selected_name = st.selectbox("Baby", options=list(baby_options.keys()))
        baby = baby_options[selected_name]
    with col2:
        meal_type = st.selectbox(
            "Meal type",
            options=MEAL_TYPES,
            format_func=lambda x: f"{MEAL_ICONS[x]} {x.capitalize()}",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Step 1: input ──────────────────────────────────────────────────────────
    if _KEY_ITEMS not in st.session_state:
        _step_indicator(1)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<div class='nb-card'>", unsafe_allow_html=True)
        raw_input = st.text_area(
            "What did the baby eat?",
            placeholder="e.g. half a banana, 2 tbsp oatmeal with apple puree",
            height=100,
            label_visibility="visible",
        )
        st.markdown(
            "<div style='font-size:0.78rem;color:#78716C;margin-top:0.25rem;'>"
            "Describe in plain language — amounts, preparation, everything you remember.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Extract food items →", disabled=not raw_input, type="primary"):
            with st.spinner("Asking Claude to extract food items…"):
                items = extract_meal(raw_input)
            with st.spinner("Looking up nutrition data…"):
                enriched: list[FoodItem] = []
                for item in items:
                    nutrition, source = lookup_nutrition(item.food_name)
                    enriched.append(
                        item.model_copy(update={"nutrition": nutrition, "source": source})
                    )
            warnings: dict[str, list[str]] = {}
            for item in enriched:
                w = check_food_safety(item.food_name, baby.age_months, baby.allergies)
                if w:
                    warnings[item.food_name] = w

            st.session_state[_KEY_ITEMS] = enriched
            st.session_state[_KEY_WARNINGS] = warnings
            st.session_state[_KEY_RAW] = raw_input
            st.session_state[_KEY_TYPE] = meal_type
            st.rerun()
        return

    # ── Step 2: review ─────────────────────────────────────────────────────────
    items: list[FoodItem] = st.session_state[_KEY_ITEMS]
    warnings: dict[str, list[str]] = st.session_state[_KEY_WARNINGS]
    any_blocked = any(is_blocked(w) for w in warnings.values())

    _step_indicator(2)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='nb-section-label'>Extracted items — please review</div>",
        unsafe_allow_html=True,
    )

    for item in items:
        item_warnings = warnings.get(item.food_name, [])
        blocked = is_blocked(item_warnings)

        if blocked:
            border = "#FECACA"
            bg = "#FEF2F2"
            status_icon = "🚫"
        elif item_warnings:
            border = "#FDE68A"
            bg = "#FFFBEB"
            status_icon = "⚠️"
        else:
            border = "#FED7AA"
            bg = "white"
            status_icon = "✅"

        qty_label = f"{item.quantity} {item.unit}"
        if item.quantity_is_estimated:
            qty_label += " <span style='font-size:0.7rem;color:#78716C;'>(est.)</span>"

        cal_line = ""
        if item.nutrition and item.nutrition.calories_kcal:
            source_badge = (
                f"<span class='nb-badge nb-badge-{'orange' if item.source != 'usda' else 'green'}'>"
                f"{'USDA' if item.source == 'usda' else 'AI est.'}</span>"
            )
            cal_line = (
                f"<div class='nb-food-meta'>"
                f"{item.nutrition.calories_kcal:.0f} kcal · "
                f"{item.nutrition.protein_g or 0:.1f}g protein per 100g &nbsp; {source_badge}"
                f"</div>"
            )

        notes_line = (
            f"<div style='font-size:0.78rem;color:#78716C;font-style:italic;'>"
            f"{item.notes}</div>"
            if item.notes
            else ""
        )

        st.markdown(
            f"""<div class='nb-food-row' style='background:{bg};border-color:{border};'>
                <div>
                    <div class='nb-food-name'>{status_icon} {item.food_name}</div>
                    <div class='nb-food-meta'>{qty_label}</div>
                    {notes_line}
                    {cal_line}
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        for w in item_warnings:
            if is_blocked([w]):
                st.error(w)
            else:
                st.warning(w)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button(
            "✅ Confirm and save",
            disabled=any_blocked,
            type="primary",
            use_container_width=True,
        ):
            meal = Meal(
                baby_id=baby.id,  # type: ignore[arg-type]
                meal_type=st.session_state[_KEY_TYPE],
                raw_input=st.session_state[_KEY_RAW],
            )
            save_meal(meal, items)
            _clear_extraction()
            st.session_state["show_totals_for"] = baby.id
            st.rerun()
    with col2:
        if st.button("✗ Cancel", use_container_width=True):
            _clear_extraction()
            st.rerun()

    if any_blocked:
        st.error("🚫 One or more items are blocked by safety rules and cannot be saved.")

    # ── Step 3: done ───────────────────────────────────────────────────────────
    if st.session_state.get("show_totals_for") == baby.id:
        _step_indicator(3)
        st.success("🎉 Meal saved! Here's today's log:")
        _render_todays_totals(baby.id, baby.name)
        if st.button("Log another meal", type="primary"):
            st.session_state.pop("show_totals_for", None)
            st.rerun()


def _render_todays_totals(baby_id: int, baby_name: str) -> None:
    rows = get_todays_food_items(baby_id)
    if not rows:
        st.info("Nothing logged today yet.")
        return

    total_cal = sum(r["calories_kcal"] or 0 for r in rows)
    total_prot = sum(r["protein_g"] or 0 for r in rows)
    total_iron = sum(r["iron_mg"] or 0 for r in rows)

    c1, c2, c3 = st.columns(3)
    c1.metric("Calories (kcal/100g)", f"{total_cal:.0f}")
    c2.metric("Protein (g/100g)", f"{total_prot:.1f}")
    c3.metric("Iron (mg/100g)", f"{total_iron:.1f}")

    st.dataframe(
        [
            {
                "Food": r["food_name"],
                "Qty": f"{r['quantity']} {r['unit']}",
                "Meal": r["meal_type"],
                "Cal/100g": f"{r['calories_kcal']:.0f}" if r["calories_kcal"] else "—",
                "Protein/100g": f"{r['protein_g']:.1f}g" if r["protein_g"] else "—",
                "Source": r["source"] or "—",
            }
            for r in rows
        ],
        use_container_width=True,
        hide_index=True,
    )
