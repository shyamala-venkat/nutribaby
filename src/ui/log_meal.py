"""Log meal page — text → extract → safety check → confirm → save."""

import streamlit as st

from src.db.models import FoodItem, Meal
from src.db.queries import get_all_babies, get_todays_food_items, save_meal
from src.llm.extractors import extract_meal
from src.nutrition.lookup import lookup_nutrition
from src.safety.rules import check_food_safety, is_blocked

MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]

# Session state keys
_KEY_ITEMS = "log_items"          # list[FoodItem] after enrichment
_KEY_WARNINGS = "log_warnings"    # dict[food_name, list[str]]
_KEY_RAW = "log_raw_input"
_KEY_TYPE = "log_meal_type"
_KEY_BABY = "log_baby_id"


def _clear_extraction() -> None:
    for key in (_KEY_ITEMS, _KEY_WARNINGS, _KEY_RAW, _KEY_TYPE):
        st.session_state.pop(key, None)


def render() -> None:
    st.header("🍽️ Log a Meal")
    st.caption("Learning project — not medical advice. Consult your pediatrician.")

    babies = get_all_babies()
    if not babies:
        st.warning("No baby profiles found. Create one on the Baby Profiles page first.")
        return

    # ── Baby + meal type selectors ───────────────────────────────────────────
    baby_options = {b.name: b for b in babies}
    selected_name = st.selectbox("Baby", options=list(baby_options.keys()))
    baby = baby_options[selected_name]

    meal_type = st.selectbox("Meal type", options=MEAL_TYPES)

    # ── Step 1: text input + Extract button ─────────────────────────────────
    if _KEY_ITEMS not in st.session_state:
        raw_input = st.text_area(
            "What did the baby eat?",
            placeholder="e.g. half a banana, 2 tbsp oatmeal with apple puree",
            height=100,
        )
        if st.button("Extract food items", disabled=not raw_input):
            with st.spinner("Extracting food items…"):
                items = extract_meal(raw_input)

            with st.spinner("Looking up nutrition…"):
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

    # ── Step 2: show extracted items + safety warnings ───────────────────────
    items: list[FoodItem] = st.session_state[_KEY_ITEMS]
    warnings: dict[str, list[str]] = st.session_state[_KEY_WARNINGS]
    any_blocked = any(is_blocked(w) for w in warnings.values())

    st.subheader("Extracted items")
    for item in items:
        item_warnings = warnings.get(item.food_name, [])
        blocked = is_blocked(item_warnings)
        icon = "🚫" if blocked else ("⚠️" if item_warnings else "✅")
        label = f"{icon} **{item.food_name}** — {item.quantity} {item.unit}"
        if item.notes:
            label += f" *({item.notes})*"
        if item.quantity_is_estimated:
            label += " *(qty estimated)*"
        st.markdown(label)

        if item.nutrition and item.nutrition.calories_kcal:
            cal = item.nutrition.calories_kcal
            prot = item.nutrition.protein_g or 0
            st.caption(f"  {cal:.0f} kcal · {prot:.1f}g protein per 100g  [{item.source}]")

        for w in item_warnings:
            if is_blocked([w]):
                st.error(w)
            else:
                st.warning(w)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        confirm_disabled = any_blocked
        if st.button("✅ Confirm and save", disabled=confirm_disabled, type="primary"):
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
        if st.button("✗ Cancel"):
            _clear_extraction()
            st.rerun()

    if any_blocked:
        st.error("One or more items are blocked by safety rules and cannot be saved.")

    # ── Step 3: today's totals (shown after save) ────────────────────────────
    if st.session_state.get("show_totals_for") == baby.id:
        st.success("Meal saved!")
        _render_todays_totals(baby.id, baby.name)
        if st.button("Log another meal"):
            st.session_state.pop("show_totals_for", None)
            st.rerun()


def _render_todays_totals(baby_id: int, baby_name: str) -> None:
    st.subheader(f"Today's food log — {baby_name}")
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
                "Prot/100g": f"{r['protein_g']:.1f}g" if r["protein_g"] else "—",
                "Source": r["source"] or "—",
            }
            for r in rows
        ],
        use_container_width=True,
        hide_index=True,
    )
