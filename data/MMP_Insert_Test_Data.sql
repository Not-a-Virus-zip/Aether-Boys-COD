PRAGMA foreign_keys = ON;

-- ============================================================
-- PREREQUISITES
-- Run MMP_MeasureType_Data.sql FIRST. Ingredient and MealIngredient have
-- foreign keys to MeasureType, and the lookups below are by unit name.
-- (If a unit name is missing from MeasureType, the JOIN silently drops that row.)
-- ============================================================

-- Each ingredient's default unit is looked up by name, so IDs don't matter.
-- fdcID is NULL on purpose (these are not real USDA IDs).
WITH v(name, tag, unit) AS (VALUES
    ('Spaghetti',         'Pasta',      'gram'),
    ('Ground Beef',       'Meat',       'gram'),
    ('Chicken Breast',    'Meat',       'gram'),
    ('Crushed Tomatoes',  'Canned',     'gram'),
    ('Onion',             'Produce',    'count'),
    ('Garlic',            'Produce',    'count'),
    ('Bell Pepper',       'Produce',    'count'),
    ('Broccoli',          'Produce',    'gram'),
    ('Olive Oil',         'Pantry',     'tablespoon'),
    ('Soy Sauce',         'Condiments', 'tablespoon'),
    ('Salsa',             'Condiments', 'cup'),
    ('Rice',              'Grains',     'cup'),
    ('Flour',             'Baking',     'cup'),
    ('Milk',              'Dairy',      'cup'),
    ('Egg',               'Dairy',      'count'),
    ('Butter',            'Dairy',      'tablespoon'),
    ('Cheddar Cheese',    'Dairy',      'ounce'),
    ('Tortillas',         'Bakery',     'count')
)
INSERT INTO Ingredient (name, tag, fdcID, measureID)
SELECT v.name, v.tag, NULL, mt.measureID
FROM v
JOIN MeasureType mt ON mt.name = v.unit;

-- ============================================================
-- MEAL
-- Plain Buttered Rice leaves tag, picture, description, and recipe NULL
-- to test the optional fields.
-- ============================================================

INSERT INTO Meal (name, tag, picture, description, recipe) VALUES
    ('Spaghetti Bolognese', 'Dinner', NULL,
     'Classic meat sauce over spaghetti.',
     '1. Brown beef with onion and garlic. 2. Add tomatoes and simmer 20 min. 3. Boil spaghetti and combine.'),
    ('Chicken Stir Fry', 'Dinner', NULL,
     'Quick chicken and vegetable stir fry over rice.',
     '1. Cook rice. 2. Sear chicken in oil. 3. Add vegetables, garlic, and soy sauce. 4. Serve over rice.'),
    ('Pancakes', 'Breakfast', NULL,
     'Fluffy weekend pancakes.',
     '1. Mix flour, milk, and egg. 2. Cook in buttered pan until golden on both sides.'),
    ('Beef Tacos', 'Dinner', NULL,
     'Seasoned ground beef tacos with cheese and salsa.',
     '1. Brown beef with onion. 2. Warm tortillas. 3. Fill with beef, cheese, and salsa.'),
    ('Plain Buttered Rice', NULL, NULL, NULL, NULL);

-- ============================================================
-- MEALINGREDIENT
-- Looks up IDs by name. Several lines use a different unit than the
-- ingredient's default (e.g. Spaghetti in ounces would be a good
-- conversion test; here Cheddar is in ounces, Flour in cups, etc.).
-- Shared ingredients (Garlic, Onion, Olive Oil, Rice, Butter, Ground Beef)
-- appear in multiple meals to test shopping-list totals.
-- ============================================================

WITH v(meal, ingredient, qty, unit) AS (VALUES
    -- Spaghetti Bolognese
    ('Spaghetti Bolognese', 'Spaghetti',        200,  'gram'),
    ('Spaghetti Bolognese', 'Ground Beef',      300,  'gram'),
    ('Spaghetti Bolognese', 'Crushed Tomatoes', 400,  'gram'),
    ('Spaghetti Bolognese', 'Onion',            1,    'count'),
    ('Spaghetti Bolognese', 'Garlic',           3,    'count'),
    ('Spaghetti Bolognese', 'Olive Oil',        1,    'tablespoon'),
    -- Chicken Stir Fry
    ('Chicken Stir Fry',    'Chicken Breast',   400,  'gram'),
    ('Chicken Stir Fry',    'Bell Pepper',      2,    'count'),
    ('Chicken Stir Fry',    'Broccoli',         250,  'gram'),
    ('Chicken Stir Fry',    'Soy Sauce',        3,    'tablespoon'),
    ('Chicken Stir Fry',    'Garlic',           2,    'count'),
    ('Chicken Stir Fry',    'Rice',             1,    'cup'),
    ('Chicken Stir Fry',    'Olive Oil',        1,    'tablespoon'),
    -- Pancakes
    ('Pancakes',            'Flour',            1.5,  'cup'),
    ('Pancakes',            'Milk',             1.25, 'cup'),
    ('Pancakes',            'Egg',              1,    'count'),
    ('Pancakes',            'Butter',           2,    'tablespoon'),
    -- Beef Tacos
    ('Beef Tacos',          'Ground Beef',      400,  'gram'),
    ('Beef Tacos',          'Tortillas',        8,    'count'),
    ('Beef Tacos',          'Cheddar Cheese',   4,    'ounce'),
    ('Beef Tacos',          'Salsa',            0.5,  'cup'),
    ('Beef Tacos',          'Onion',            0.5,  'count'),
    -- Plain Buttered Rice (minimal meal)
    ('Plain Buttered Rice', 'Rice',             1,    'cup'),
    ('Plain Buttered Rice', 'Butter',           1,    'tablespoon')
)
INSERT INTO MealIngredient (mealID, ingredientID, qty, measureID)
SELECT m.mealID, i.ingredientID, v.qty, mt.measureID
FROM v
JOIN Meal m         ON m.name  = v.meal
JOIN Ingredient i   ON i.name  = v.ingredient
JOIN MeasureType mt ON mt.name = v.unit;

-- ============================================================
-- VIRTUALPANTRY
-- Mix of cases: Olive Oil is stored in milliliter (its default unit is
-- tablespoon) to test unit conversion, and Salsa is 0 to test the
-- qtyHave >= 0 rule. Spaghetti is short of what a double batch needs, etc.
-- ============================================================

WITH v(ingredient, qty, unit) AS (VALUES
    ('Spaghetti', 500,  'gram'),
    ('Olive Oil', 120,  'milliliter'),
    ('Rice',      3,    'cup'),
    ('Garlic',    5,    'count'),
    ('Onion',     2,    'count'),
    ('Flour',     4,    'cup'),
    ('Milk',      16,   'fluid_ounce'),
    ('Egg',       6,    'count'),
    ('Butter',    4,    'tablespoon'),
    ('Salsa',     0,    'cup')
)
INSERT INTO VirtualPantry (ingredientID, qtyHave, measureID)
SELECT i.ingredientID, v.qty, mt.measureID
FROM v
JOIN Ingredient i   ON i.name  = v.ingredient
JOIN MeasureType mt ON mt.name = v.unit;

-- ============================================================
-- SANITY CHECK: should return 24 rows (MealIngredient)
-- ============================================================
-- SELECT m.name AS meal, i.name AS ingredient, mi.qty, mt.name AS unit
-- FROM MealIngredient mi
-- JOIN Meal m         ON m.mealID = mi.mealID
-- JOIN Ingredient i   ON i.ingredientID = mi.ingredientID
-- JOIN MeasureType mt ON mt.measureID = mi.measureID
-- ORDER BY m.name, i.name;
