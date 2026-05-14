"""Pydantic models for database rows and LLM I/O."""

import json
from datetime import UTC, date, datetime

from pydantic import BaseModel, Field, field_validator


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


class Baby(BaseModel):
    """A baby profile."""

    id: int | None = None
    name: str
    dob: date
    allergies: list[str] = Field(default_factory=list)
    diet_type: str = "omnivore"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("allergies", mode="before")
    @classmethod
    def parse_allergies(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return json.loads(v)
        return v  # type: ignore[return-value]

    @property
    def age_months(self) -> int:
        today = date.today()
        months = (today.year - self.dob.year) * 12 + (today.month - self.dob.month)
        if today.day < self.dob.day:
            months -= 1
        return max(0, months)

    @property
    def age_display(self) -> str:
        m = self.age_months
        if m < 1:
            return "< 1 month"
        if m < 12:
            return f"{m} month{'s' if m != 1 else ''}"
        years, rem = divmod(m, 12)
        parts = [f"{years} year{'s' if years != 1 else ''}"]
        if rem:
            parts.append(f"{rem} month{'s' if rem != 1 else ''}")
        return " ".join(parts)


class Meal(BaseModel):
    """A logged meal."""

    id: int | None = None
    baby_id: int
    meal_type: str
    logged_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    raw_input: str
