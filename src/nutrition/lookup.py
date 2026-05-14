"""Hybrid nutrition lookup: SQLite cache → USDA API → Claude estimate."""

import logging

from src.db.models import NutritionInfo
from src.db.queries import cache_nutrition, get_cached_nutrition
from src.llm.client import tool_chat
from src.llm.prompts import NUTRITION_ESTIMATE_SYSTEM
from src.nutrition.usda_client import search_usda

logger = logging.getLogger(__name__)

_NUTRITION_TOOL: dict = {
    "name": "record_nutrition",
    "description": "Record estimated nutritional values per 100g of a food.",
    "input_schema": {
        "type": "object",
        "properties": {
            "calories_kcal": {"type": "number", "description": "Energy in kcal"},
            "protein_g": {"type": "number", "description": "Protein in grams"},
            "fat_g": {"type": "number", "description": "Total fat in grams"},
            "carbs_g": {"type": "number", "description": "Carbohydrates in grams"},
            "fiber_g": {"type": "number", "description": "Dietary fiber in grams"},
            "iron_mg": {"type": "number", "description": "Iron in milligrams"},
            "calcium_mg": {"type": "number", "description": "Calcium in milligrams"},
            "zinc_mg": {"type": "number", "description": "Zinc in milligrams"},
            "vitamin_d_mcg": {"type": "number", "description": "Vitamin D in micrograms"},
            "vitamin_c_mg": {"type": "number", "description": "Vitamin C in milligrams"},
        },
        "required": ["calories_kcal", "protein_g", "fat_g", "carbs_g"],
    },
}


def lookup_nutrition(food_name: str) -> tuple[NutritionInfo, str]:
    """Return nutrition info for a food, trying cache → USDA → Claude in order.

    Args:
        food_name: Plain food name, e.g. 'banana', 'khichdi'.

    Returns:
        (NutritionInfo, source) where source is 'cache', 'usda', or 'llm_estimate'.
    """
    # 1. Cache hit
    cached = get_cached_nutrition(food_name)
    if cached:
        logger.info("Cache hit for '%s'", food_name)
        nutrition, original_source = cached
        return nutrition, "cache"

    # 2. USDA lookup
    usda_result = search_usda(food_name)
    if usda_result:
        cache_nutrition(food_name, usda_result, "usda")
        return usda_result, "usda"

    # 3. Claude fallback
    logger.info("USDA miss for '%s' — falling back to Claude estimate", food_name)
    llm_result = _estimate_with_claude(food_name)
    cache_nutrition(food_name, llm_result, "llm_estimate")
    return llm_result, "llm_estimate"


def _estimate_with_claude(food_name: str) -> NutritionInfo:
    """Ask Claude to estimate nutrition per 100g for a food not found in USDA."""
    result = tool_chat(
        messages=[{"role": "user", "content": f"Food: {food_name}"}],
        tools=[_NUTRITION_TOOL],
        tool_name="record_nutrition",
        system=NUTRITION_ESTIMATE_SYSTEM,
    )
    return NutritionInfo(**result)
