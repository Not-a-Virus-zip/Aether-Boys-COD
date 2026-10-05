PRAGMA foreign_keys = ON;  --This needs to be run everytime the python file connects to it.

DROP TABLE IF EXISTS VirtualPantry;
DROP TABLE IF EXISTS Ingredient;
DROP TABLE IF EXISTS Tag;
DROP TABLE IF EXISTS MeasureType;

CREATE TABLE MeasureType(
    measureID integer primary key,
    name TEXT NOT NULL,
    plural TEXT NOT NULL,
    abbreviation TEXT NOT NULL,
    dimension TEXT NOT NULL CHECK (dimension IN ('Mass', 'Volume', 'Count'))
);

CREATE TABLE Tag(
    tagID INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    tagType TEXT NOT NULL CHECK (tagType IN ('Meal', 'Ingredient'))
);

CREATE TABLE Ingredient(
    ingredientID INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    tagID INTEGER,
    fdcID INTEGER,
    measureID INTEGER NOT NULL,
    FOREIGN KEY(tagID) REFERENCES Tag(tagID)
        ON UPDATE CASCADE ON DELETE SET NULL,
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
