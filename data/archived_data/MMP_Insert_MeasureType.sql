-- Seed data for MeasureType
-- Run after MMP Create Tables.sql
-- Dimension values used: 'Volume', 'Mass', 'Count'

INSERT INTO MeasureType (name, plural, abbreviation, dimension) VALUES
    -- Volume (US)
    ('teaspoon',     'teaspoons',     'tsp',    'Volume'),
    ('tablespoon',   'tablespoons',   'tbsp',   'Volume'),
    ('fluid ounce',  'fluid ounces',  'fl oz',  'Volume'),
    ('cup',          'cups',          'cup',    'Volume'),
    ('pint',         'pints',         'pt',     'Volume'),
    ('quart',        'quarts',        'qt',     'Volume'),
    ('gallon',       'gallons',       'gal',    'Volume'),

    -- Volume (metric)
    ('milliliter',   'milliliters',   'mL',     'Volume'),
    ('liter',        'liters',        'L',      'Volume'),

    -- Mass (US)
    ('ounce',        'ounces',        'oz',     'Mass'),
    ('pound',        'pounds',        'lb',     'Mass'),

    -- Mass (metric)
    ('gram',         'grams',         'g',      'Mass'),
    ('kilogram',     'kilograms',     'kg',     'Mass'),

    -- Count
    ('piece',        'pieces',        'pc',     'Count'),
    ('clove',        'cloves',        'clove',  'Count'),
    ('slice',        'slices',        'slice',  'Count'),
    ('can',          'cans',          'can',    'Count'),
    ('pinch',        'pinches',       'pinch',  'Count');
