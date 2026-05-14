-- Cached nutrition lookups. food_name is normalized to lowercase.
CREATE TABLE IF NOT EXISTS food_cache (
    food_name    TEXT PRIMARY KEY,
    nutrition_json TEXT NOT NULL,       -- JSON-serialized NutritionInfo
    source       TEXT NOT NULL,         -- 'usda' or 'llm_estimate'
    fetched_at   TEXT NOT NULL          -- ISO-8601 UTC timestamp
);
