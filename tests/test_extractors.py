"""Integration tests for meal extraction. Requires ANTHROPIC_API_KEY to run."""

import os

import pytest
from dotenv import load_dotenv

load_dotenv()

from src.llm.extractors import extract_meal  # noqa: E402

pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)


def _assert_valid_items(items, min_count: int = 1) -> None:
    """Shared assertions for any extraction result."""
    assert len(items) >= min_count, f"Expected >= {min_count} items, got {len(items)}"
    for item in items:
        assert item.food_name.strip(), "food_name must not be empty"
        assert item.quantity > 0, "quantity must be positive"
        assert item.unit.strip(), "unit must not be empty"


def test_simple_single_item():
    """Plain single food with an explicit quantity."""
    items = extract_meal("half a banana")
    _assert_valid_items(items)
    names = [i.food_name.lower() for i in items]
    assert any("banana" in n for n in names)


def test_multi_item_explicit_quantities():
    """Two foods with different units in one description."""
    items = extract_meal("2 tbsp oatmeal with some apple puree")
    _assert_valid_items(items, min_count=2)


def test_ethnic_food_vague_quantity():
    """Ethnic dish with a vague quantity should set quantity_is_estimated."""
    items = extract_meal("a small bowl of khichdi")
    _assert_valid_items(items)
    assert any(i.quantity_is_estimated for i in items), (
        "Vague quantity 'a small bowl' should set quantity_is_estimated=True"
    )


def test_fully_vague_quantities():
    """'Some rice and dal' — both quantities are estimates."""
    items = extract_meal("some rice and dal")
    _assert_valid_items(items, min_count=2)
    assert all(i.quantity_is_estimated for i in items), (
        "Both items should be estimated when quantities are completely vague"
    )


def test_complex_multi_item_with_prep_notes():
    """Multiple items with preparation details captured in notes."""
    items = extract_meal("a few bites of scrambled eggs and toast with butter")
    _assert_valid_items(items, min_count=2)
    names = [i.food_name.lower() for i in items]
    assert any("egg" in n for n in names)
    assert any("toast" in n or "bread" in n for n in names)
