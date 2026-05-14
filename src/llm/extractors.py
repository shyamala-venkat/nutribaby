"""Meal extraction: raw text → structured list of FoodItems via Claude tool use."""

from src.db.models import FoodItem
from src.llm.client import tool_chat
from src.llm.prompts import MEAL_EXTRACTION_SYSTEM

# Tool definition — the schema Claude must conform to when it calls record_food_items.
_EXTRACT_TOOL: dict = {
    "name": "record_food_items",
    "description": "Record all food items parsed from the meal description.",
    "input_schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "description": "One entry per distinct food item.",
                "items": {
                    "type": "object",
                    "required": ["food_name", "quantity", "unit", "quantity_is_estimated"],
                    "properties": {
                        "food_name": {"type": "string"},
                        "quantity": {"type": "number", "exclusiveMinimum": 0},
                        "unit": {"type": "string"},
                        "notes": {"type": "string"},
                        "quantity_is_estimated": {"type": "boolean"},
                    },
                },
            }
        },
        "required": ["items"],
    },
}


def extract_meal(raw_text: str) -> list[FoodItem]:
    """Parse a free-text meal description into structured food items.

    Args:
        raw_text: Natural language meal description from the parent,
            e.g. "half a banana and 2 tbsp oatmeal".

    Returns:
        List of FoodItem objects. Empty list if nothing parseable was found.
    """
    result = tool_chat(
        messages=[{"role": "user", "content": raw_text}],
        tools=[_EXTRACT_TOOL],
        tool_name="record_food_items",
        system=MEAL_EXTRACTION_SYSTEM,
    )
    return [FoodItem(**item) for item in result.get("items", [])]
