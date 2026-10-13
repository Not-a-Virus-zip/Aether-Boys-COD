# Purpose: Get data to and from the database.
import sqlite3 as sql
from .database_tools import SelectDB, get_connection


type Name = str
type Tag = str

# This class covers all requests that the Ingredient screen will make
class IngredientQuery(SelectDB):

    # Variables needed for SELECT
    select_query = 'SELECT i.ingredientID, i.name, t.name ' \
                  'FROM Ingredient as i ' \
                  'LEFT JOIN Tag as t ' \
                      'ON i.tagID = t.tagID '
    accepted_filters = {'ingredient': 'i.name', 'tag': 't.name', 'id': 'i.ingredientID'}
    accepted_sorts = {'ingredient': 'i.name', 'tag': 't.name', 'date': 'i.ingredientID'}

    # Stores new data in the database
    @staticmethod
    def run_insert(ingredient_name, tag_id, measure_id) -> bool:
        try:
            with get_connection() as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Ingredient(name, tagID, measureID) VALUES (?, ?, ?)", 
                            (ingredient_name, tag_id, measure_id,))
            return True
        except sql.IntegrityError as e:
            print(f'{e}: There was an ID that is invalid...\nTagID: {tag_id}\nMeasureID: {measure_id}')
            return False

    # Updates an existing entry
    @staticmethod
    def run_update(ingredient_id, ingredient_name, tag_id, measure_id):
        try: 
            with get_connection() as con:
                cur = con.cursor()
                cur.execute('UPDATE Ingredient ' \
                            'SET name = ?, tagID = ?, measureID = ?' \
                            'WHERE ingredientID = ?;',
                            (ingredient_name, tag_id, measure_id, ingredient_id))
            return True
        except sql.IntegrityError as e:
            print(f'{e}: There was an invalid ID given. Please check!')
            return False


# This class covers all requests that the Virtual Pantry screen will make
class VirtualPantryQuery(SelectDB):

    # Variables needed for SELECT
    select_query = 'SELECT vp.ingredientID, i.name, vp.qtyHave, mt.Abbreviation ' \
                  'FROM VirtualPantry as vp ' \
                  'JOIN MeasureType as mt ' \
                      'ON vp.measureID = mt.measureID ' \
                  'JOIN Ingredient as i ' \
                      'ON vp.ingredientID = i.ingredientID '
    accepted_filters = {'ingredient': 'i.name', 'id': 'vp.ingredientID'}
    accepted_sorts = {'ingredient': 'i.name', 'date': 'vp.ingredientID'}

    # Stores new data in the database
    @staticmethod
    def run_insert(ingredient_id: str, qty_owned: int, measure_id: str) -> bool:
        try:
            with get_connection() as con:
                cur = con.cursor()
                cur.execute("INSERT INTO VirtualPantry (ingredientID, qtyHave, measureID) VALUES (?, ?, ?)", 
                            (ingredient_id, qty_owned, measure_id,))
            return True
        except sql.IntegrityError as e:
            print(f'{e} The Ingredient was ID#: {ingredient_id!r}!')
            return False

    # Updates an existing entry
    @staticmethod
    def run_update(ingredient_id: str, qty: str, measure_id: str) -> bool:
        try:
            with get_connection() as con:
                cur = con.cursor()
                cur.execute('UPDATE VirtualPantry ' \
                            'SET qtyHave = ?, measureID = ? ' \
                            'WHERE ingredientID = ?;',
                            (qty, measure_id, ingredient_id))
            return True
        except sql.IntegrityError as e:
            print(f'{e}: There was an invalid ID given. Please check!')
            return False


class TagDB(SelectDB):

    select_query = 'SELECT *' \
                   'From Tag'
    accepted_filters = {'name': 'name', 'type': 'tagType', 'id': 'tagID'}
    accepted_sorts = {'name': 'name', 'type': 'tagType', 'date': 'tagID'}


class MeasureTypeDB(SelectDB):

        select_query = 'SELECT *' \
                       'FROM MeasureType'
        accepted_filters = {'id': 'measureID', 'name': 'name', 'dimension': 'dimension'}
        accepted_sorts = {'date': 'measureID', 'name': 'name', 'dimension': 'dimension'}



# TODO: Add a class for tag and measure type. Both only need selects
