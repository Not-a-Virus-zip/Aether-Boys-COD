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
    def run_insert(ingredient_name: str, tag: str, measure_id: int):
        valid_check = IngredientQuery.run_select(filter_column='unit', filter_value=measure_id)
        if valid_check is None:
            raise InvalidFK()
        with get_connection() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Ingredient(name, tag, measureID) VALUES (?, ?, ?)", 
                        (ingredient_name, tag, measure_id,))
        

    # Updates an existing entry
    @staticmethod
    def run_update(ingredient_id: int, ingredient_name: str, tag: str, measure_id: int):
        valid_check = IngredientQuery.run_select(filter_column='unit', filter_value=measure_id)
        if valid_check is None:
            raise InvalidFK('Measure Type')
        try: 
            with get_connection() as con:
                cur = con.cursor()
                cur.execute('UPDATE Ingredient ' \
                            'SET name = ?, tag = ?, measureID = ?' \
                            'WHERE ingredientID = ?;',
                            (ingredient_name, tag, measure_id, ingredient_id))
        except sql.IntegrityError as e:
            print(f'{e}: There was an invalid ID given. Please check!')


    @staticmethod
    def run_get_tags(filter_value: str | None = None) -> list[tuple[str]]:
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
    def run_insert(ingredient_id: str, qty_owned: float, measure_id: str) -> bool:
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
                print(f"Adding {ingredient_id} {qty} {measure_id}")
            return True
        except sql.IntegrityError as e:
            print(f'{e}: There was an invalid ID given for measure {measure_id!r}. Please check!')
            return False

class MeasureTypeQuery(SelectDB):

    select_query = 'SELECT * ' \
                   'FROM MeasureType '
    accepted_filters = {'name': 'name','id': 'measureID'}
    accepted_sorts = {'name': 'name', 'date': 'measureID'}

class MealQuery(SelectDB):

    select_query = 'SELECT * ' \
                   'FROM Meal '

    accepted_filters = {'name' : 'name', 'id': 'mealID', 'tag': 'tag'}
    accepted_sorts = {'name' : 'name', 'date': 'mealID', 'tag': 'tag'}

    # TODO: This is not done. I'm getting distracted with making errors
    @staticmethod
    def run_insert(name: str, 
                   tag: str | None = None, 
                   picture: str | None = None, 
                   description: str | None = None, 
                   recipe : str | None = None
                   ):
        with get_connection() as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO Meal(name, tag, picture, description, recipe) VALUES (?, ?, ?, ?, ?)', 
                            (name, tag, picture, description, recipe))
            except sql.IntegrityError as e: 
                print()
        

        

    @staticmethod
    def run_update():
        pass


class MealIngredientQuery(SelectDB):
    pass


# Errors for data validation
class DatabaseErrors(Exception): 
    """Base class for this library"""

class InvalidFK(DatabaseErrors):
    def __init__(self, value_type, value):
        self.value_type = value_type
        self.value = value

    def __str__(self):
        return f'Invalid {self.value_type} given!'