-- Seed data for Tag
-- Run after MMP Create Tables.sql
-- tagType must be 'Meal' or 'Ingredient'

INSERT INTO Tag (name, tagType) VALUES
    -- Meal tags (a meal can have several)
    ('Breakfast',      'Meal'),
    ('Lunch',          'Meal'),
    ('Dinner',         'Meal'),
    ('Snack',          'Meal'),
    ('Dessert',        'Meal'),
    ('Quick',          'Meal'),
    ('Budget-Friendly','Meal'),
    ('Meal Prep',      'Meal'),
    ('Vegetarian',     'Meal'),
    ('Vegan',          'Meal'),
    ('Gluten-Free',    'Meal'),
    ('Kid-Friendly',   'Meal'),

    -- Ingredient tags (food categories; an ingredient has one)
    ('Produce',        'Ingredient'),
    ('Meat',           'Ingredient'),
    ('Seafood',        'Ingredient'),
    ('Dairy & Eggs',   'Ingredient'),
    ('Grains & Pasta', 'Ingredient'),
    ('Bakery',         'Ingredient'),
    ('Baking',         'Ingredient'),
    ('Spices & Herbs', 'Ingredient'),
    ('Oils & Vinegars','Ingredient'),
    ('Condiments & Sauces', 'Ingredient'),
    ('Canned & Jarred','Ingredient'),
    ('Frozen',         'Ingredient'),
    ('Beverages',      'Ingredient'),
    ('Snacks',         'Ingredient'),
    ('Other',          'Ingredient');
