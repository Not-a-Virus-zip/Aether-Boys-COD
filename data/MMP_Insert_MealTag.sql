-- Seed data for MealTag
-- Run after MMP_Create_Tables.sql
-- MealTag holds tags for meals only (a meal can have several).
-- Ingredient categories are NOT stored here; they are plain text in Ingredient.tag.

INSERT INTO MealTag (name) VALUES
    ('Breakfast'),
    ('Lunch'),
    ('Dinner'),
    ('Snack'),
    ('Dessert'),
    ('Quick'),
    ('Budget-Friendly'),
    ('Meal Prep'),
    ('Vegetarian'),
    ('Vegan'),
    ('Gluten-Free'),
    ('Kid-Friendly');
