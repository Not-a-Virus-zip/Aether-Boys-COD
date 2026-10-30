PRAGMA foreign_keys = ON;

WITH v(date, time, meal) AS (VALUES
    ('2026-11-07', '19:00', 'Beef Tacos'),
    ('2026-11-03', '18:00', 'Spaghetti Bolognese'),
    ('2026-11-01', '18:30', 'Beef Tacos'),
    ('2026-11-14', '18:30', 'Chicken Stir Fry'),
    ('2026-11-07', '09:00', 'Pancakes'),
    ('2026-10-28', '18:00', 'Spaghetti Bolognese'),   -- past event
    ('2026-11-05', '18:30', 'Chicken Stir Fry'),
    ('2026-11-01', '09:00', 'Pancakes'),
    ('2026-11-10', '18:00', 'Spaghetti Bolognese'),
    ('2026-11-07', '12:30', 'Hamburger'),             -- meal with no ingredients
    ('2026-11-04', '12:00', 'Plain Buttered Rice'),
    ('2026-12-01', '18:00', 'Beef Tacos')             -- far-future event
)
INSERT INTO Event (date, time, mealID)
SELECT v.date, v.time, m.mealID
FROM v
JOIN Meal m ON m.name = v.meal;