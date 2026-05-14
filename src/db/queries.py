"""SQLite helpers: connection management + food_cache read/write."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from src.db.models import NutritionInfo

_SCHEMA = Path(__file__).with_name("schema.sql").read_text()
_DEFAULT_DB = Path(__file__).parents[2] / "data" / "nutribaby.db"


def get_connection(db_path: Path = _DEFAULT_DB) -> sqlite3.Connection:
    """Open (and auto-initialize) the SQLite database.

    Args:
        db_path: Path to the .db file. Created if it doesn't exist.

    Returns:
        An open sqlite3 connection with row_factory set.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def get_cached_nutrition(
    food_name: str,
    db_path: Path = _DEFAULT_DB,
) -> tuple[NutritionInfo, str] | None:
    """Return cached nutrition + source for a food, or None if not cached.

    Args:
        food_name: Food name (normalized to lowercase internally).
        db_path: Path to the database file.

    Returns:
        (NutritionInfo, source_string) tuple, or None on cache miss.
    """
    key = food_name.strip().lower()
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT nutrition_json, source FROM food_cache WHERE food_name = ?", (key,)
        ).fetchone()
    if row is None:
        return None
    return NutritionInfo.model_validate_json(row["nutrition_json"]), row["source"]


def cache_nutrition(
    food_name: str,
    nutrition: NutritionInfo,
    source: str,
    db_path: Path = _DEFAULT_DB,
) -> None:
    """Upsert a nutrition entry into the cache.

    Args:
        food_name: Food name (normalized to lowercase internally).
        nutrition: NutritionInfo to store.
        source: 'usda' or 'llm_estimate'.
        db_path: Path to the database file.
    """
    key = food_name.strip().lower()
    now = datetime.now(UTC).isoformat()
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO food_cache (food_name, nutrition_json, source, fetched_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(food_name) DO UPDATE SET
                nutrition_json = excluded.nutrition_json,
                source = excluded.source,
                fetched_at = excluded.fetched_at
            """,
            (key, nutrition.model_dump_json(), source, now),
        )
        conn.commit()
