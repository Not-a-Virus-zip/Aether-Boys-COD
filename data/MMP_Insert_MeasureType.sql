PRAGMA foreign_keys = ON;

-- ============================================================
-- MEASURETYPE seed data
-- Run this BEFORE MMP_Test_Data.sql (Ingredient and MealIngredient
-- have foreign keys to MeasureType).
-- name = canonical Pint unit name (checked with ureg.parse_units).
-- abbreviation = display text only (not meant to be parsed by Pint).
-- 'count' replaces 'each' because Pint has no 'each' unit.
-- ============================================================

INSERT OR IGNORE INTO MeasureType (name, abbreviation) VALUES
    -- mass
    ('gram',        'g'),
    ('kilogram',    'kg'),
    ('ounce',       'oz'),
    ('pound',       'lb'),
    -- volume
    ('milliliter',  'mL'),
    ('liter',       'L'),
    ('teaspoon',    'tsp'),
    ('tablespoon',  'tbsp'),
    ('fluid_ounce', 'fl oz'),
    ('cup',         'cup'),
    ('pint',        'pt'),
    ('quart',       'qt'),
    ('gallon',      'gal'),
    -- countable items
    ('count',       'ct');
