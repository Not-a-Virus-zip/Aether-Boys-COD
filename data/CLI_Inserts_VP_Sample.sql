.bail on
PRAGMA foreign_keys = ON;
-- 1. Making Schema
.read MMP_Create_Tables.sql;

-- 2. Parents
.read MMP_Insert_MeasureType.sql;
.read MMP_Insert_MealTag.sql;

-- 3. Ingredients (Needs MeasureType only; its category is plain text)
.read MMP_Insert_Ingredient.sql;

-- 4. Sample pantry
.read MMP_Insert_VirtualPantry.sql;
