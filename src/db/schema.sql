CREATE TABLE IF NOT EXISTS babies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    dob         TEXT NOT NULL,              -- YYYY-MM-DD
    allergies   TEXT NOT NULL DEFAULT '[]', -- JSON array of strings
    diet_type   TEXT NOT NULL DEFAULT 'omnivore',
    created_at  TEXT NOT NULL               -- ISO-8601 UTC
);

CREATE TABLE IF NOT EXISTS meals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    baby_id     INTEGER NOT NULL REFERENCES babies(id),
    meal_type   TEXT NOT NULL,              -- breakfast, lunch, dinner, snack
    logged_at   TEXT NOT NULL,              -- ISO-8601 UTC
    raw_input   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS food_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_id         INTEGER NOT NULL REFERENCES meals(id),
    food_name       TEXT NOT NULL,
    quantity        REAL NOT NULL,
    unit            TEXT NOT NULL,
    nutrition_json  TEXT,                   -- JSON-serialized NutritionInfo, nullable
    source          TEXT                    -- 'usda', 'llm_estimate', 'cache'
);

-- Cached nutrition lookups. food_name is normalized to lowercase.
CREATE TABLE IF NOT EXISTS food_cache (
    food_name    TEXT PRIMARY KEY,
    nutrition_json TEXT NOT NULL,       -- JSON-serialized NutritionInfo
    source       TEXT NOT NULL,         -- 'usda' or 'llm_estimate'
    fetched_at   TEXT NOT NULL          -- ISO-8601 UTC timestamp
);
