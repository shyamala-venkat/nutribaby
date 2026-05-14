"""Pydantic models for database rows and LLM I/O."""

from pydantic import BaseModel, Field


class NutritionInfo(BaseModel):
    """Nutritional values per 100g of a food item."""

    calories_kcal: float | None = None
    protein_g: float | None = None
    fat_g: float | None = None
    carbs_g: float | None = None
    fiber_g: float | None = None
    iron_mg: float | None = None
    calcium_mg: float | None = None
    zinc_mg: float | None = None
    vitamin_d_mcg: float | None = None
    vitamin_c_mg: float | None = None


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
    nutrition: NutritionInfo | None = Field(
        default=None, description="Nutritional values per 100g, populated after lookup"
    )
    source: str | None = Field(
        default=None, description="Data source: 'usda', 'llm_estimate', or 'cache'"
    )
