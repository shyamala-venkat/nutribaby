"""RDA targets, unit-to-grams conversion, and daily progress computation."""

import json
from pathlib import Path

_RDA_PATH = Path(__file__).parents[2] / "data" / "rda_by_age.json"

# Unit → approximate grams
_UNIT_GRAMS: dict[str, float] = {
    "g": 1.0,
    "ml": 1.0,
    "tsp": 5.0,
    "tbsp": 15.0,
    "cup": 240.0,
    "whole": 100.0,   # overridden per food below
    "piece": 50.0,
    "slice": 30.0,
    "small bowl": 150.0,
    "medium bowl": 250.0,
    "bites": 20.0,
    "bite": 20.0,
}

# Food-specific gram weights for "whole" unit
_WHOLE_OVERRIDES: dict[str, float] = {
    "banana": 120.0,
    "egg": 50.0,
    "apple": 150.0,
}

_TRACKED_NUTRIENTS = [
    "calories_kcal",
    "protein_g",
    "iron_mg",
    "calcium_mg",
    "zinc_mg",
    "vitamin_d_mcg",
    "vitamin_c_mg",
]

NUTRIENT_LABELS: dict[str, str] = {
    "calories_kcal": "Calories (kcal)",
    "protein_g": "Protein (g)",
    "iron_mg": "Iron (mg)",
    "calcium_mg": "Calcium (mg)",
    "zinc_mg": "Zinc (mg)",
    "vitamin_d_mcg": "Vitamin D (mcg)",
    "vitamin_c_mg": "Vitamin C (mg)",
}


def to_grams(quantity: float, unit: str, food_name: str = "") -> float:
    """Convert a quantity + unit to approximate grams.

    Args:
        quantity: Numeric amount.
        unit: Unit string (case-insensitive).
        food_name: Used to apply food-specific overrides for 'whole' unit.

    Returns:
        Estimated weight in grams.
    """
    u = unit.strip().lower()
    if u == "whole":
        for food_key, grams in _WHOLE_OVERRIDES.items():
            if food_key in food_name.lower():
                return quantity * grams
    return quantity * _UNIT_GRAMS.get(u, 100.0)


def get_rda(age_months: int) -> dict[str, float]:
    """Return the RDA targets for a given age in months.

    Falls back to the oldest band if age exceeds 36 months.

    Args:
        age_months: Baby's current age in months.

    Returns:
        Dict mapping nutrient field names to daily target values.
    """
    bands: list[dict] = json.loads(_RDA_PATH.read_text())
    for band in bands:
        if band["min_months"] <= age_months <= band["max_months"]:
            return band["targets"]
    return bands[-1]["targets"]


def get_rda_label(age_months: int) -> str:
    """Return the human-readable age band label for display."""
    bands: list[dict] = json.loads(_RDA_PATH.read_text())
    for band in bands:
        if band["min_months"] <= age_months <= band["max_months"]:
            return band["label"]
    return bands[-1]["label"]


def compute_daily_progress(
    food_rows: list[dict],
    age_months: int,
) -> dict[str, dict]:
    """Compute actual daily nutrient intake vs RDA targets.

    Args:
        food_rows: Rows from get_todays_food_items — must include a 'nutrition'
            key with the full NutritionInfo dict.
        age_months: Baby's current age in months.

    Returns:
        Dict keyed by nutrient name. Each value has:
            actual (float), target (float), pct (0.0–2.0 capped), label (str).
    """
    targets = get_rda(age_months)
    totals: dict[str, float] = {k: 0.0 for k in _TRACKED_NUTRIENTS}

    for row in food_rows:
        nutrition: dict = row.get("nutrition") or {}
        grams = to_grams(row["quantity"], row["unit"], row["food_name"])
        scale = grams / 100.0
        for nutrient in _TRACKED_NUTRIENTS:
            val = nutrition.get(nutrient)
            if val is not None:
                totals[nutrient] += scale * val

    result: dict[str, dict] = {}
    for nutrient in _TRACKED_NUTRIENTS:
        target = targets.get(nutrient, 0.0)
        actual = totals[nutrient]
        pct = min(actual / target, 2.0) if target > 0 else 0.0
        result[nutrient] = {
            "actual": actual,
            "target": target,
            "pct": pct,
            "label": NUTRIENT_LABELS[nutrient],
        }
    return result
