-- Seed data for Ingredient
-- Run AFTER MMP Create Tables.sql, MMP_Insert_MeasureType.sql, and MMP_Insert_Tag.sql
-- Tags and units are looked up by name, so this doesn't depend on ID numbers.
-- fdcID is left NULL (to be filled in from the USDA FoodData Central API).

WITH src(name, tagName, unitName) AS (VALUES
    -- Produce
    ('onion',               'Produce', 'piece'),
    ('garlic',              'Produce', 'clove'),
    ('tomato',              'Produce', 'piece'),
    ('potato',              'Produce', 'piece'),
    ('sweet potato',        'Produce', 'piece'),
    ('carrot',              'Produce', 'piece'),
    ('celery',              'Produce', 'piece'),
    ('bell pepper',         'Produce', 'piece'),
    ('broccoli',            'Produce', 'pound'),
    ('spinach',             'Produce', 'ounce'),
    ('lettuce',             'Produce', 'piece'),
    ('cucumber',            'Produce', 'piece'),
    ('zucchini',            'Produce', 'piece'),
    ('mushroom',            'Produce', 'ounce'),
    ('green onion',         'Produce', 'piece'),
    ('lemon',               'Produce', 'piece'),
    ('lime',                'Produce', 'piece'),
    ('apple',               'Produce', 'piece'),
    ('banana',              'Produce', 'piece'),
    ('avocado',             'Produce', 'piece'),

    -- Meat
    ('chicken breast',      'Meat', 'pound'),
    ('ground beef',         'Meat', 'pound'),
    ('ground turkey',       'Meat', 'pound'),
    ('steak',               'Meat', 'pound'),
    ('pork chop',           'Meat', 'pound'),
    ('sausage',             'Meat', 'pound'),
    ('bacon',               'Meat', 'slice'),

    -- Seafood
    ('salmon',              'Seafood', 'pound'),
    ('shrimp',              'Seafood', 'pound'),

    -- Dairy & Eggs
    ('milk',                'Dairy & Eggs', 'cup'),
    ('butter',              'Dairy & Eggs', 'tablespoon'),
    ('egg',                 'Dairy & Eggs', 'piece'),
    ('cheddar cheese',      'Dairy & Eggs', 'ounce'),
    ('mozzarella cheese',   'Dairy & Eggs', 'ounce'),
    ('parmesan cheese',     'Dairy & Eggs', 'ounce'),
    ('cream cheese',        'Dairy & Eggs', 'ounce'),
    ('heavy cream',         'Dairy & Eggs', 'cup'),
    ('sour cream',          'Dairy & Eggs', 'cup'),
    ('yogurt',              'Dairy & Eggs', 'cup'),

    -- Grains & Pasta
    ('white rice',          'Grains & Pasta', 'cup'),
    ('spaghetti',           'Grains & Pasta', 'ounce'),
    ('penne pasta',         'Grains & Pasta', 'ounce'),
    ('rolled oats',         'Grains & Pasta', 'cup'),
    ('quinoa',              'Grains & Pasta', 'cup'),
    ('flour tortilla',      'Grains & Pasta', 'piece'),

    -- Bakery
    ('bread',               'Bakery', 'slice'),
    ('hamburger bun',       'Bakery', 'piece'),

    -- Baking
    ('all-purpose flour',   'Baking', 'cup'),
    ('white sugar',         'Baking', 'cup'),
    ('brown sugar',         'Baking', 'cup'),
    ('baking powder',       'Baking', 'teaspoon'),
    ('baking soda',         'Baking', 'teaspoon'),
    ('vanilla extract',     'Baking', 'teaspoon'),
    ('cocoa powder',        'Baking', 'tablespoon'),

    -- Spices & Herbs
    ('salt',                'Spices & Herbs', 'teaspoon'),
    ('black pepper',        'Spices & Herbs', 'teaspoon'),
    ('paprika',             'Spices & Herbs', 'teaspoon'),
    ('cumin',               'Spices & Herbs', 'teaspoon'),
    ('chili powder',        'Spices & Herbs', 'teaspoon'),
    ('oregano',             'Spices & Herbs', 'teaspoon'),
    ('basil',               'Spices & Herbs', 'teaspoon'),
    ('cinnamon',            'Spices & Herbs', 'teaspoon'),
    ('garlic powder',       'Spices & Herbs', 'teaspoon'),
    ('onion powder',        'Spices & Herbs', 'teaspoon'),

    -- Oils & Vinegars
    ('olive oil',           'Oils & Vinegars', 'tablespoon'),
    ('vegetable oil',       'Oils & Vinegars', 'tablespoon'),
    ('balsamic vinegar',    'Oils & Vinegars', 'tablespoon'),

    -- Condiments & Sauces
    ('ketchup',             'Condiments & Sauces', 'tablespoon'),
    ('mayonnaise',          'Condiments & Sauces', 'tablespoon'),
    ('mustard',             'Condiments & Sauces', 'tablespoon'),
    ('soy sauce',           'Condiments & Sauces', 'tablespoon'),
    ('hot sauce',           'Condiments & Sauces', 'teaspoon'),
    ('tomato sauce',        'Condiments & Sauces', 'cup'),
    ('salsa',               'Condiments & Sauces', 'cup'),

    -- Canned & Jarred
    ('black beans',         'Canned & Jarred', 'can'),
    ('diced tomatoes',      'Canned & Jarred', 'can'),
    ('canned tuna',         'Canned & Jarred', 'can'),
    ('chicken broth',       'Canned & Jarred', 'cup'),
    ('peanut butter',       'Canned & Jarred', 'tablespoon'),
    ('honey',               'Canned & Jarred', 'tablespoon'),

    -- Frozen
    ('frozen peas',         'Frozen', 'cup'),
    ('frozen mixed vegetables', 'Frozen', 'cup'),

    -- Beverages
    ('orange juice',        'Beverages', 'cup'),
    ('ground coffee',       'Beverages', 'tablespoon'),

    -- Snacks
    ('tortilla chips',      'Snacks', 'ounce')
)
INSERT INTO Ingredient (name, tagID, measureID)
SELECT s.name, t.tagID, m.measureID
FROM src AS s
LEFT JOIN Tag AS t         ON t.name = s.tagName AND t.tagType = 'Ingredient'
LEFT JOIN MeasureType AS m ON m.name = s.unitName;
