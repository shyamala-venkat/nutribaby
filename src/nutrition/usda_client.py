"""USDA FoodData Central API client.

Searches Foundation and SR Legacy foods only — lab-verified nutrient data,
no branded products.
"""

import logging
import os

import httpx

from src.db.models import NutritionInfo

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
_DATA_TYPES = ["Foundation", "SR Legacy"]

# USDA nutrient ID → NutritionInfo field name
_NUTRIENT_MAP: dict[int, str] = {
    1008: "calories_kcal",
    1003: "protein_g",
    1004: "fat_g",
    1005: "carbs_g",
    1079: "fiber_g",
    1089: "iron_mg",
    1087: "calcium_mg",
    1095: "zinc_mg",
    1114: "vitamin_d_mcg",
    1162: "vitamin_c_mg",
}


def search_usda(food_name: str) -> NutritionInfo | None:
    """Search USDA FoodData Central and return nutrition per 100g.

    Tries Foundation foods first, falls back to SR Legacy.
    Returns None if nothing is found or the API key is missing.

    Args:
        food_name: Plain food name, e.g. 'banana', 'cooked lentils'.

    Returns:
        NutritionInfo with values per 100g, or None on miss/error.
    """
    api_key = os.getenv("USDA_API_KEY")
    if not api_key:
        logger.warning("USDA_API_KEY not set — skipping USDA lookup")
        return None

    try:
        response = httpx.get(
            f"{_BASE_URL}/foods/search",
            params={
                "query": food_name,
                "api_key": api_key,
                "dataType": ",".join(_DATA_TYPES),
                "pageSize": 5,
            },
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as e:
        logger.warning("USDA API error for '%s': %s", food_name, e)
        return None

    foods = response.json().get("foods", [])
    if not foods:
        logger.info("USDA: no results for '%s'", food_name)
        return None

    # Prefer Foundation over SR Legacy
    ordered = sorted(foods, key=lambda f: 0 if f.get("dataType") == "Foundation" else 1)
    best = ordered[0]
    logger.info(
        "USDA: matched '%s' → '%s' (%s)", food_name, best.get("description"), best.get("dataType")
    )

    return _parse_nutrients(best.get("foodNutrients", []))


def _parse_nutrients(raw_nutrients: list[dict]) -> NutritionInfo:
    """Extract the nutrients we care about from a USDA food nutrients list."""
    values: dict[str, float] = {}
    for nutrient in raw_nutrients:
        nid = nutrient.get("nutrientId")
        field = _NUTRIENT_MAP.get(nid)
        if field and "value" in nutrient:
            values[field] = float(nutrient["value"])
    return NutritionInfo(**values)
