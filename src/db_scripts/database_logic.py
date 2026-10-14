# Purpose: Get data to and from the database.
import sqlite3 as sql
from .database_tools import SelectDB, get_connection


type Name = str
type Tag = str

# This class covers all requests that the Ingredient screen will make
class IngredientQuery(SelectDB):

    # Variables needed for SELECT
    select_query = 'SELECT i.ingredientID, i.name, i.tag, mt.name ' \
                  'FROM Ingredient as i ' \
                  'LEFT JOIN MeasureType as mt ' \
                      'ON i.measureID = mt.measureID '
    accepted_filters = {'ingredient': 'i.name', 'tag': 'i.tag', 'id': 'i.ingredientID', 'unit': 'mt.name'}
    accepted_sorts = {'ingredient': 'i.name', 'tag': 'i.name', 'date': 'i.ingredientID', 'unit': 'mt.name'}

    # Stores new data in the database
    @staticmethod
    def run_insert(ingredient_name: str, tag: str, measure_id: int) -> bool:
        try:
            with get_connection() as con:
                cur = con.cursor()
                cur.execute("INSERT INTO Ingredient(name, tagID, measureID) VALUES (?, ?, ?)", 
                            (ingredient_name, tag, measure_id,))
            return True
        except sql.IntegrityError as e:
            print(f'{e}: There was an ID that is invalid...\nTagID: {tag}\nMeasureID: {measure_id}')
            return False

    # Updates an existing entry
    @staticmethod
    def run_update(ingredient_id: int, ingredient_name: str, tag: int, measure_id: int):
        try: 
            with get_connection() as con:
                cur = con.cursor()
                cur.execute('UPDATE Ingredient ' \
                            'SET name = ?, tag = ?, measureID = ?' \
                            'WHERE ingredientID = ?;',
                            (ingredient_name, tag, measure_id, ingredient_id))
            return True
        except sql.IntegrityError as e:
            print(f'{e}: There was an invalid ID given. Please check!')
            return False

    @staticmethod
    def run_get_tags(filter_value: str | None = None):
        query = ('SELECT DISTINCT tag '
                'FROM Ingredient '
                "WHERE tag IS NOT NULL AND TRIM(tag) <> '' ")
        filter_tuple = ()

        if filter_value is not None:
            query += 'AND tag LIKE ? '
            filter_tuple = (f'%{filter_value}%',)
        query += 'ORDER BY tag;'

        with get_connection() as con:
            return con.execute(query, filter_tuple).fetchall()


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


# class TagQuery(SelectDB):

#     select_query = 'SELECT *' \
#                    'From Tag '
#     accepted_filters = {'name': 'name', 'type': 'tagType', 'id': 'tagID'}
#     accepted_sorts = {'name': 'name', 'type': 'tagType', 'date': 'tagID'}

#     @staticmethod
#     def run_insert(name: str, tag_type: str):
#         try:
#             with get_connection() as con:
#                 cur = con.cursor()
#                 cur.execute('INSERT INTO Tag (name, tagType) VALUES (?,?)',
#                             (name,tag_type))
#         except sql.IntegrityError as e:
#             raise f'{e}: Type must be \'Ingredient\' or \'Meal\''



class MeasureTypeQuery(SelectDB):

        select_query = 'SELECT *' \
                       'FROM MeasureType '
        accepted_filters = {'name': 'name', 'dimension': 'dimension', 'id': 'measureID'}
        accepted_sorts = {'name': 'name', 'dimension': 'dimension', 'date': 'measureID'}

