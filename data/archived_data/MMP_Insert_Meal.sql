PRAGMA foreign_keys = ON;

-- ============================================================
-- PREREQUISITES: MeasureType and Ingredient
-- MealIngredient has foreign keys to these, so they must exist first.
-- Skip or adjust this block if you already have your own rows.
-- Unit names should match whatever your unit-conversion library expects.
-- ============================================================

INSERT OR IGNORE INTO MeasureType (name) VALUES
    ('gram'), ('milliliter'), ('cup'), ('tablespoon'),
    ('teaspoon'), ('ounce'), ('pound'), ('each');

-- Each ingredient's default unit is looked up by name, so IDs don't matter.
-- fdcID is NULL on purpose (these are not real USDA IDs).
WITH v(name, tag, unit) AS (VALUES
    ('Spaghetti',         'Pasta',      'gram'),
    ('Ground Beef',       'Meat',       'gram'),
    ('Chicken Breast',    'Meat',       'gram'),
    ('Crushed Tomatoes',  'Canned',     'gram'),
    ('Onion',             'Produce',    'each'),
    ('Garlic',            'Produce',    'each'),
    ('Bell Pepper',       'Produce',    'each'),
    ('Broccoli',          'Produce',    'gram'),
    ('Olive Oil',         'Pantry',     'tablespoon'),
    ('Soy Sauce',         'Condiments', 'tablespoon'),
    ('Salsa',             'Condiments', 'cup'),
    ('Rice',              'Grains',     'cup'),
    ('Flour',             'Baking',     'cup'),
    ('Milk',              'Dairy',      'cup'),
    ('Egg',               'Dairy',      'each'),
    ('Butter',            'Dairy',      'tablespoon'),
    ('Cheddar Cheese',    'Dairy',      'ounce'),
    ('Tortillas',         'Bakery',     'each')
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
    ('Spaghetti Bolognese', 'Onion',            1,    'each'),
    ('Spaghetti Bolognese', 'Garlic',           3,    'each'),
    ('Spaghetti Bolognese', 'Olive Oil',        1,    'tablespoon'),
    -- Chicken Stir Fry
    ('Chicken Stir Fry',    'Chicken Breast',   400,  'gram'),
    ('Chicken Stir Fry',    'Bell Pepper',      2,    'each'),
    ('Chicken Stir Fry',    'Broccoli',         250,  'gram'),
    ('Chicken Stir Fry',    'Soy Sauce',        3,    'tablespoon'),
    ('Chicken Stir Fry',    'Garlic',           2,    'each'),
    ('Chicken Stir Fry',    'Rice',             1,    'cup'),
    ('Chicken Stir Fry',    'Olive Oil',        1,    'tablespoon'),
    -- Pancakes
    ('Pancakes',            'Flour',            1.5,  'cup'),
    ('Pancakes',            'Milk',             1.25, 'cup'),
    ('Pancakes',            'Egg',              1,    'each'),
    ('Pancakes',            'Butter',           2,    'tablespoon'),
    -- Beef Tacos
    ('Beef Tacos',          'Ground Beef',      400,  'gram'),
    ('Beef Tacos',          'Tortillas',        8,    'each'),
    ('Beef Tacos',          'Cheddar Cheese',   4,    'ounce'),
    ('Beef Tacos',          'Salsa',            0.5,  'cup'),
    ('Beef Tacos',          'Onion',            0.5,  'each'),
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
-- SANITY CHECK: should return 24 rows
-- ============================================================
-- SELECT m.name AS meal, i.name AS ingredient, mi.qty, mt.name AS unit
-- FROM MealIngredient mi
-- JOIN Meal m         ON m.mealID = mi.mealID
-- JOIN Ingredient i   ON i.ingredientID = mi.ingredientID
-- JOIN MeasureType mt ON mt.measureID = mi.measureID
-- ORDER BY m.name, i.name;
