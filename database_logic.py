import sqlite3 as sql
from scripts.database_tools import get_connection

type Name = str
type Tag = str

# This class covers all requests that the Ingredient screen will make
class IngredientLogic:
    # Default query needed
    _query = 'SELECT i.name, t.name ' \
            'FROM Ingredient as i ' \
            'LEFT JOIN Tag as t ' \
                'ON i.tagID = t.tagID '
    # This is the default order that the ingredients come out as.
    @staticmethod
    def get_default_ingredients(self) -> list[tuple[Name, Tag]]:
        with get_connection() as con:
            cur = con.cursor()
            ingredients = cur.execute(IngredientLogic._query + 'ORDER BY i.name asc')
        return ingredients.fetchall()

type Quantity = int
type Ingredient = str
type Abbreviation = str

# This class covers all requests that the Virtual Pantry screen will make
class VirtualPantry:
    # This is the default order that the Virtual Pantry comes out as.
    @staticmethod
    def get_default_virtual_pantry() -> list[tuple[Ingredient, Quantity, Abbreviation]]:
        with get_connection() as con:
            cur = con.cursor()
            ingredients = cur.execute('SELECT i.name, vp.qtyHave, mt.Abbreviation ' \
                                      'FROM VirtualPantry as vp ' \
                                      'JOIN MeasureType as mt ' \
                                          'ON vp.measureID = mt.measureID ' \
                                      'JOIN Ingredient as i ' \
                                          'ON vp.ingredientID = i.ingredientID ' \
                                      'ORDER BY i.name asc ')
        return ingredients.fetchall()

print(IngredientLogic.get_default_ingredients())