PRAGMA foreign_keys = ON;  --This needs to be run everytime the python file connects to it.

DROP TABLE IF EXISTS VirtualPantry;
DROP TABLE IF EXISTS Ingredient;
DROP TABLE IF EXISTS MealTag;
DROP TABLE IF EXISTS Tag;   -- legacy name, removed so old databases get cleaned up
DROP TABLE IF EXISTS MeasureType;

CREATE TABLE MeasureType(
    measureID integer primary key,
    name TEXT NOT NULL,
    plural TEXT NOT NULL,
    abbreviation TEXT NOT NULL,
    dimension TEXT NOT NULL CHECK (dimension IN ('Mass', 'Volume', 'Count'))
);

-- Meal tags only. An ingredient's category is stored as plain text in Ingredient.tag.
CREATE TABLE MealTag(
    tagID INTEGER PRIMARY KEY,
    name TEXT NOT NULL
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
