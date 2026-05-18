"""Baby profile page — create and view baby profiles."""

from datetime import date

import streamlit as st

from src.db.models import Baby
from src.db.queries import create_baby, get_all_babies, update_baby
from src.safety.rules import COMMON_ALLERGENS
from src.ui.styles import inject

DIET_TYPES = ["omnivore", "vegetarian", "vegan", "pescatarian"]
DIET_ICONS = {"omnivore": "🍗", "vegetarian": "🥦", "vegan": "🌱", "pescatarian": "🐟"}


def render() -> None:
    inject()

    st.markdown(
        "<div class='nb-section-label'>Manage profiles</div>", unsafe_allow_html=True
    )
    st.markdown("## 👶 Baby Profiles")

    babies = get_all_babies()

    # ── Existing profiles ─────────────────────────────────────────────────────
    if babies:
        for baby in babies:
            diet_icon = DIET_ICONS.get(baby.diet_type, "🍽️")
            allergy_chips = " ".join(
                f"<span class='nb-badge nb-badge-red'>{a}</span>"
                for a in baby.allergies
            ) or "<span class='nb-badge nb-badge-green'>None listed</span>"

            with st.expander(
                f"{diet_icon} **{baby.name}** — {baby.age_display}", expanded=False
            ):
                st.markdown(
                    f"<div style='margin-bottom:0.75rem;'>Allergies: {allergy_chips}</div>",
                    unsafe_allow_html=True,
                )
                with st.form(key=f"edit_baby_{baby.id}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("Name", value=baby.name)
                    with col2:
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
                    if st.form_submit_button("Save changes", type="primary"):
                        updated = baby.model_copy(
                            update={
                                "name": name,
                                "dob": dob,
                                "allergies": allergies,
                                "diet_type": diet_type,
                            }
                        )
                        update_baby(updated)
                        st.success(f"✅ Saved changes for **{name}**.")
                        st.rerun()
    else:
        st.markdown("""
        <div class="nb-card" style="text-align:center; padding: 2rem;">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">👶</div>
            <div style="color:#78716C; font-size:0.9rem;">
                No profiles yet. Create your first baby below.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Add new baby ──────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        "<div class='nb-section-label'>Add new</div>", unsafe_allow_html=True
    )
    st.markdown("#### Create a baby profile")

    st.markdown("<div class='nb-card'>", unsafe_allow_html=True)
    with st.form("new_baby"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Baby's name")
        with col2:
            dob = st.date_input(
                "Date of birth",
                value=None,
                min_value=date(2020, 1, 1),
                max_value=date.today(),
            )
        allergies = st.multiselect(
            "Known allergies",
            options=COMMON_ALLERGENS,
            help="Select all that apply. You can update this later.",
        )
        diet_type = st.selectbox("Diet type", options=DIET_TYPES)

        submitted = st.form_submit_button("Create profile", type="primary")
        if submitted:
            if not name:
                st.error("Please enter a name.")
            elif dob is None:
                st.error("Please enter a date of birth.")
            else:
                baby = Baby(name=name, dob=dob, allergies=allergies, diet_type=diet_type)
                new_id = create_baby(baby)
                st.success(f"✅ Profile created for **{name}** (id={new_id}). Head to **Log Meal** to get started!")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
