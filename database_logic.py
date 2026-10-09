# Purpose: Get data to and from the database.
import sqlite3 as sql
from scripts.database_tools import get_connection

type Name = str
type Tag = str

# This class covers all requests that the Ingredient screen will make
class IngredientLogic:

    # Returns the order of the query
    def _get_order(order: str, asc: bool) -> str:
        if order.lower() == 'ingredient':
            order_sql = 'ORDER BY i.name '  # Order by ingredient name
        else:
            order_sql = 'ORDER BY t.name '  # Order by tag

        if asc:
            order_sql += 'ASC '
        else:
            order_sql += 'DESC '
        return order_sql
    
    # This method will give Ingredient data
    # This method also assumes that filter data will only be sent when both filter arguments are not none
    @staticmethod
    def get_data(filter_column = None, filter_value = None, order = 'ingredient', asc = True) -> list[tuple[Name, Tag]]:
        
        query = 'SELECT i.name, t.name ' \
                'FROM Ingredient as i ' \
                'LEFT JOIN Tag as t ' \
                    'ON i.tagID = t.tagID '

        # filter_column is expected 'ingredient' or 'tag'
        if filter_column is not None and filter_value is not None:
            query += 'WHERE '
            if filter_column.lower() == 'ingredient':
                query += 'i.name LIKE '
            elif filter_column.lower() == 'tag':
                query += 't.name LIKE '
            query += '? ' + IngredientLogic._get_order(order, asc)
            with get_connection() as con:
                cur = con.cursor()
                ingredients = cur.execute(query, (f'%{filter_value}%',))
            return ingredients.fetchall()
        else:
            query + IngredientLogic._get_order(order, asc)
            with get_connection() as con:
                cur = con.cursor()
                ingredients = cur.execute(query)
            return ingredients.fetchall()

type Quantity = int
type Ingredient = str
type Abbreviation = str

# This class covers all requests that the Virtual Pantry screen will make
class VirtualPantry:
    # Default query needed
    _BASE_QUERY = 'SELECT i.name, vp.qtyHave, mt.Abbreviation ' \
                  'FROM VirtualPantry as vp ' \
                  'JOIN MeasureType as mt ' \
                      'ON vp.measureID = mt.measureID ' \
                  'JOIN Ingredient as i ' \
                      'ON vp.ingredientID = i.ingredientID '
    
    # This is the default order that the Virtual Pantry comes out as.
    @staticmethod
    def get_default_data() -> list[tuple[Ingredient, Quantity, Abbreviation]]:
        with get_connection() as con:
            cur = con.cursor()
            ingredients = cur.execute(VirtualPantry._BASE_QUERY + 'ORDER BY i.name asc ')
        return ingredients.fetchall()
