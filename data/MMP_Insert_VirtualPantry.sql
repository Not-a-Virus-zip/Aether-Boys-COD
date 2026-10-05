-- Sample seed data for VirtualPantry (test data, not required for the app)
-- Run AFTER MMP Create Tables.sql, MMP_Insert_MeasureType.sql, and MMP_Insert_Ingredient.sql
-- Ingredients and units are looked up by name, so this doesn't depend on ID numbers.

WITH src(ingName, qtyHave, unitName) AS (VALUES
    -- Produce
    ('onion',               3,    'piece'),
    ('garlic',              8,    'clove'),
    ('potato',              5,    'piece'),
    ('carrot',              4,    'piece'),

    -- Meat
    ('chicken breast',      2,    'pound'),
    ('ground beef',         1.5,  'pound'),

    -- Dairy & Eggs
    ('egg',                 12,   'piece'),
    ('milk',                4,    'cup'),
    ('butter',              8,    'tablespoon'),
    ('cheddar cheese',      8,    'ounce'),

    -- Grains, bread, baking
    ('white rice',          6,    'cup'),
    ('spaghetti',           16,   'ounce'),
    ('bread',               10,   'slice'),
    ('all-purpose flour',   5,    'cup'),
    ('white sugar',         3,    'cup'),

    -- Spices, oils, condiments
    ('salt',                50,   'teaspoon'),
    ('black pepper',        30,   'teaspoon'),
    ('olive oil',           20,   'tablespoon'),
    ('ketchup',             16,   'tablespoon'),

    -- Canned
    ('black beans',         2,    'can')
)
INSERT INTO VirtualPantry (ingredientID, qtyHave, measureID)
SELECT i.ingredientID, s.qtyHave, m.measureID
FROM src AS s
JOIN Ingredient AS i       ON i.name = s.ingName
LEFT JOIN MeasureType AS m ON m.name = s.unitName;
