"""Pydantic models for database rows and LLM I/O."""

from pydantic import BaseModel, Field


class FoodItem(BaseModel):
    """A single food item extracted from a meal description."""

    food_name: str = Field(description="Name of the food, e.g. 'banana', 'khichdi'")
    quantity: float = Field(gt=0, description="Numeric amount")
    unit: str = Field(description="Unit of measurement, e.g. 'whole', 'tbsp', 'small bowl'")
    notes: str | None = Field(
        default=None, description="Preparation notes, e.g. 'mashed', 'with butter'"
    )
    quantity_is_estimated: bool = Field(
        default=False,
        description="True when the original text was vague and quantity was estimated",
    )
