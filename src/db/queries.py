"""SQLite helpers: connection management, baby CRUD, meal logging, food_cache."""

import json
import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path

from src.db.models import Baby, FoodItem, Meal, NutritionInfo

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


# ---------------------------------------------------------------------------
# Baby CRUD
# ---------------------------------------------------------------------------


def create_baby(baby: Baby, db_path: Path = _DEFAULT_DB) -> int:
    """Insert a new baby and return its assigned id.

    Args:
        baby: Baby model (id field is ignored).
        db_path: Path to the database file.

    Returns:
        The new baby's integer id.
    """
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO babies (name, dob, allergies, diet_type, created_at) VALUES (?,?,?,?,?)",
            (
                baby.name,
                baby.dob.isoformat(),
                json.dumps(baby.allergies),
                baby.diet_type,
                baby.created_at.isoformat(),
            ),
        )
        conn.commit()
        return cursor.lastrowid  # type: ignore[return-value]


def get_all_babies(db_path: Path = _DEFAULT_DB) -> list[Baby]:
    """Return all baby profiles ordered by creation date."""
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM babies ORDER BY created_at ASC").fetchall()
    return [_row_to_baby(r) for r in rows]


def get_baby(baby_id: int, db_path: Path = _DEFAULT_DB) -> Baby | None:
    """Return a single baby by id, or None if not found."""
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM babies WHERE id = ?", (baby_id,)).fetchone()
    return _row_to_baby(row) if row else None


def update_baby(baby: Baby, db_path: Path = _DEFAULT_DB) -> None:
    """Update an existing baby profile (matched by id).

    Args:
        baby: Baby model with a non-None id.
        db_path: Path to the database file.
    """
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE babies SET name=?, dob=?, allergies=?, diet_type=? WHERE id=?",
            (
                baby.name,
                baby.dob.isoformat(),
                json.dumps(baby.allergies),
                baby.diet_type,
                baby.id,
            ),
        )
        conn.commit()


def _row_to_baby(row: sqlite3.Row) -> Baby:
    return Baby(
        id=row["id"],
        name=row["name"],
        dob=date.fromisoformat(row["dob"]),
        allergies=json.loads(row["allergies"]),
        diet_type=row["diet_type"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


# ---------------------------------------------------------------------------
# Meal logging
# ---------------------------------------------------------------------------


def save_meal(
    meal: Meal,
    food_items: list[FoodItem],
    db_path: Path = _DEFAULT_DB,
) -> int:
    """Persist a meal and its food items in a single transaction.

    Args:
        meal: Meal model (id field is ignored).
        food_items: Enriched FoodItem list (with nutrition + source populated).
        db_path: Path to the database file.

    Returns:
        The new meal's integer id.
    """
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO meals (baby_id, meal_type, logged_at, raw_input) VALUES (?,?,?,?)",
            (meal.baby_id, meal.meal_type, meal.logged_at.isoformat(), meal.raw_input),
        )
        meal_id = cursor.lastrowid
        for item in food_items:
            nutrition_json = item.nutrition.model_dump_json() if item.nutrition else None
            conn.execute(
                """INSERT INTO food_items
                   (meal_id, food_name, quantity, unit, nutrition_json, source)
                   VALUES (?,?,?,?,?,?)""",
                (meal_id, item.food_name, item.quantity, item.unit, nutrition_json, item.source),
            )
        conn.commit()
    return meal_id  # type: ignore[return-value]


def get_todays_food_items(
    baby_id: int,
    db_path: Path = _DEFAULT_DB,
) -> list[dict]:
    """Return all food items logged today for a baby as plain dicts.

    Args:
        baby_id: The baby's id.
        db_path: Path to the database file.

    Returns:
        List of dicts with keys: food_name, quantity, unit, meal_type,
        source, nutrition (full dict), plus convenience keys calories_kcal,
        protein_g, iron_mg for backward compatibility.
    """
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT fi.food_name, fi.quantity, fi.unit, fi.nutrition_json,
                   fi.source, m.meal_type
            FROM food_items fi
            JOIN meals m ON fi.meal_id = m.id
            WHERE m.baby_id = ?
              AND substr(m.logged_at, 1, 10) = strftime('%Y-%m-%d', 'now')
            ORDER BY m.logged_at ASC
            """,
            (baby_id,),
        ).fetchall()

    result = []
    for row in rows:
        nutrition: dict = json.loads(row["nutrition_json"]) if row["nutrition_json"] else {}
        result.append(
            {
                "food_name": row["food_name"],
                "quantity": row["quantity"],
                "unit": row["unit"],
                "meal_type": row["meal_type"],
                "source": row["source"],
                "nutrition": nutrition,
                # convenience keys kept for log_meal.py totals
                "calories_kcal": nutrition.get("calories_kcal"),
                "protein_g": nutrition.get("protein_g"),
                "iron_mg": nutrition.get("iron_mg"),
            }
        )
    return result


# ---------------------------------------------------------------------------
# Nutrition cache
# ---------------------------------------------------------------------------


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
