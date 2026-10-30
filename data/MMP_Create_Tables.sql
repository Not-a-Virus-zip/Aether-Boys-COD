PRAGMA foreign_keys = ON;  --This needs to be run everytime the python file connects to it.

DROP TABLE IF EXISTS MealIngredient;
DROP TABLE IF EXISTS Meal;
DROP TABLE IF EXISTS VirtualPantry;
DROP TABLE IF EXISTS Ingredient;
DROP TABLE IF EXISTS MealTag; -- legacy table, removed so old databases get cleaned up
DROP TABLE IF EXISTS Tag;   -- legacy table, removed so old databases get cleaned up
DROP TABLE IF EXISTS MeasureType;
DROP TABLE IF EXISTS Event;


CREATE TABLE MeasureType(
    measureID integer primary key,
    name TEXT NOT NULL UNIQUE,
    abbreviation TEXT NOT NULL
);

CREATE TABLE Ingredient(
    ingredientID INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    tag TEXT,
    fdcID INTEGER,
    measureID INTEGER NOT NULL,
    FOREIGN KEY(measureID) REFERENCES MeasureType(measureID)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE VirtualPantry(
    ingredientID INTEGER PRIMARY KEY,
    qtyHave REAL NOT NULL CHECK (qtyHave >= 0),
    measureID INTEGER NOT NULL,
    FOREIGN KEY(ingredientID) REFERENCES Ingredient(ingredientID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(measureID) REFERENCES MeasureType(measureID)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Meal(
    mealID INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    tag TEXT,
    picture TEXT,
    description TEXT,
    recipe TEXT
);

CREATE TABLE MealIngredient (
    mealID INTEGER NOT NULL,
    ingredientID INTEGER NOT NULL,
    qty REAL NOT NULL CHECK (qty > 0),
    measureID INTEGER NOT NULL,
    PRIMARY KEY (mealID, ingredientID),
    FOREIGN KEY(mealID) REFERENCES Meal(mealID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(ingredientID) REFERENCES Ingredient(ingredientID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY(measureID) REFERENCES MeasureType(measureID)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Event (
    eventID INTEGER PRIMARY KEY,
    date TEXT NOT NULL,  --'YYYY-MM-DD'
    time TEXT NOT NULL,  --'HH:MM' (24-HOUR)
    mealID INTEGER NOT NULL,
    FOREIGN KEY(mealID) REFERENCES Meal(mealID)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX idx_event_date_time ON Event(date, time);  -- Sorted copy of date values for fast searching when using WHERE 



-- SELECT e.eventID, e.date, e.time, m.name, m.name
-- FROM Event AS e 
-- JOIN Meal AS m 
--     ON e.mealID = m.mealID 
-- BETWEEN ? AND ?