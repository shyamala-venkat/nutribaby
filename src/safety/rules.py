"""Hard-coded food safety rules. These run as filters — never rely on prompts alone."""

COMMON_ALLERGENS = [
    "milk",
    "eggs",
    "peanuts",
    "tree nuts",
    "wheat",
    "gluten",
    "soy",
    "fish",
    "shellfish",
    "sesame",
]

_HONEY_TERMS = {"honey"}
_NUT_TERMS = {
    "almond", "walnut", "cashew", "pecan", "pistachio",
    "hazelnut", "macadamia", "brazil nut", "pine nut",
}


def check_food_safety(
    food_name: str,
    age_months: int,
    allergies: list[str],
) -> list[str]:
    """Return a list of safety warnings for a food item.

    An empty list means no issues found. Warnings must be shown to the user
    and blocked items must not be saved without explicit override.

    Args:
        food_name: The food name to check (case-insensitive).
        age_months: Baby's current age in months.
        allergies: List of allergens from the baby's profile.

    Returns:
        List of human-readable warning strings. Empty = safe.
    """
    warnings: list[str] = []
    name_lower = food_name.lower()

    # Honey → botulism risk for < 12 months
    if age_months < 12 and any(term in name_lower for term in _HONEY_TERMS):
        warnings.append(
            f"Honey is not safe for babies under 12 months (botulism risk). "
            f"{food_name!r} cannot be logged."
        )

    # Whole nuts → choking hazard for < 48 months
    if age_months < 48 and any(term in name_lower for term in _NUT_TERMS):
        warnings.append(
            f"Whole nuts are a choking hazard for babies under 4 years. "
            f"Consider ground or finely chopped form for {food_name!r}."
        )

    # Allergy cross-check
    for allergen in allergies:
        if allergen.lower() in name_lower:
            warnings.append(
                f"{food_name!r} may contain {allergen!r} (listed in baby's allergy profile)."
            )

    return warnings


def is_blocked(warnings: list[str]) -> bool:
    """Return True if any warning is a hard block (not just advisory)."""
    return any("cannot be logged" in w for w in warnings)
