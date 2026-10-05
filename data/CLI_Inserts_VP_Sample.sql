.bail on
PRAGMA foreign_keys = ON;
-- 1. Making Schema
.read MMP_Create_Tables.sql;

-- 2. Parents
.read MMP_Insert_MeasureType.sql;
.read MMP_Insert_Tag.sql;

-- 3. Ingredients (Needs Tag and MeasureType)
.read MMP_Insert_Ingredient.sql;

-- 4. Sample pantry
.read MMP_Insert_VirtualPantry.sql;
