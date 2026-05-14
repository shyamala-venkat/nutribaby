"""Baby profile page — create and view baby profiles."""

from datetime import date

import streamlit as st

from src.db.models import Baby
from src.db.queries import create_baby, get_all_babies, update_baby
from src.safety.rules import COMMON_ALLERGENS

DIET_TYPES = ["omnivore", "vegetarian", "vegan", "pescatarian"]


def render() -> None:
    st.header("👶 Baby Profiles")

    babies = get_all_babies()

    # ── Existing profiles ────────────────────────────────────────────────────
    if babies:
        for baby in babies:
            with st.expander(f"{baby.name} — {baby.age_display}", expanded=False):
                with st.form(key=f"edit_baby_{baby.id}"):
                    name = st.text_input("Name", value=baby.name)
                    dob = st.date_input(
                        "Date of birth",
                        value=baby.dob,
                        min_value=date(2020, 1, 1),
                        max_value=date.today(),
                    )
                    allergies = st.multiselect(
                        "Known allergies",
                        options=COMMON_ALLERGENS,
                        default=baby.allergies,
                    )
                    diet_type = st.selectbox(
                        "Diet type",
                        options=DIET_TYPES,
                        index=DIET_TYPES.index(baby.diet_type)
                        if baby.diet_type in DIET_TYPES
                        else 0,
                    )
                    if st.form_submit_button("Save changes"):
                        updated = baby.model_copy(
                            update={
                                "name": name,
                                "dob": dob,
                                "allergies": allergies,
                                "diet_type": diet_type,
                            }
                        )
                        update_baby(updated)
                        st.success(f"Saved changes for {name}.")
                        st.rerun()
    else:
        st.info("No baby profiles yet. Create one below.")

    # ── Add new baby ─────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Add a new baby")
    with st.form("new_baby"):
        name = st.text_input("Name")
        dob = st.date_input(
            "Date of birth",
            value=None,
            min_value=date(2020, 1, 1),
            max_value=date.today(),
        )
        allergies = st.multiselect("Known allergies", options=COMMON_ALLERGENS)
        diet_type = st.selectbox("Diet type", options=DIET_TYPES)

        if st.form_submit_button("Create profile"):
            if not name:
                st.error("Name is required.")
            elif dob is None:
                st.error("Date of birth is required.")
            else:
                baby = Baby(name=name, dob=dob, allergies=allergies, diet_type=diet_type)
                new_id = create_baby(baby)
                st.success(f"Created profile for {name} (id={new_id}).")
                st.rerun()
