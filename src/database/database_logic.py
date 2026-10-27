# Purpose: Get data to and from the database.
import sqlite3 as sql

from .database_tools import SelectDB, get_connection
from .errors import QueryInvalidFK


type Name = str
type Tag = str

# This class covers all requests that the Ingredient screen will make
class IngredientQuery(SelectDB):

    # Variables needed for SELECT
    select_query = 'SELECT i.ingredientID, i.name, i.tag, i.measureID, mt.name ' \
                   'FROM Ingredient as i ' \
                   'LEFT JOIN MeasureType as mt ' \
                       'ON i.measureID = mt.measureID '
    accepted_filters = {'name': 'i.name', 'tag': 'i.tag', 'id': 'i.ingredientID', 'unit': 'mt.name'}
    accepted_sorts = {'name': 'i.name', 'tag': 'i.tag', 'date': 'i.ingredientID', 'unit': 'mt.name'}

    # Variables needed for DELETE
    delete_table_name = 'Ingredient'
    delete_id_name = 'ingredientID'

    # Stores new data in the database
    @staticmethod
    def run_insert(ingredient_name: str, tag: str | None, measure_id: int | str):
        valid_check = IngredientQuery.run_select(filter_column='unit', filter_value=str(measure_id))
        if valid_check is None:
            raise QueryInvalidFK('Measure Type', measure_id)
        with get_connection() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Ingredient(name, tag, measureID) VALUES (?, ?, ?)", 
                        (ingredient_name, tag, measure_id,))
        

    # Updates an existing entry
    @staticmethod
    def run_update(ingredient_id: int, ingredient_name: str, tag: str | None, measure_id: int | str):
        valid_check = IngredientQuery.run_select(filter_column='unit', filter_value=str(measure_id))
        if valid_check is None:
            raise QueryInvalidFK('Measure Type', measure_id)
        try: 
            with get_connection() as con:
                cur = con.cursor()
                cur.execute('UPDATE Ingredient ' \
                            'SET name = ?, tag = ?, measureID = ?' \
                            'WHERE ingredientID = ?;',
                            (ingredient_name, tag, measure_id, ingredient_id))
        except sql.IntegrityError as e:
            print(f'{e}: There was an invalid ID given. Please check!')


    # Runs a select query on all ingredient tags
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
    select_query = 'SELECT vp.ingredientID, i.name, vp.qtyHave, mt.measureID, mt.name, mt.Abbreviation ' \
                  'FROM VirtualPantry as vp ' \
                  'JOIN MeasureType as mt ' \
                      'ON vp.measureID = mt.measureID ' \
                  'JOIN Ingredient as i ' \
                      'ON vp.ingredientID = i.ingredientID '
    accepted_filters = {'ingredient': 'i.name', 'id': 'vp.ingredientID'}
    accepted_sorts = {'ingredient': 'i.name', 'date': 'vp.ingredientID'}

    delete_table_name = 'VirtualPantry'
    delete_id_name = 'ingredientID'

    # Stores new data in the database
    @staticmethod
    def run_insert(ingredient_id: int, qty_owned: float, measure_id: str):
        try:
            with get_connection() as con:
                cur = con.cursor()
                cur.execute("INSERT INTO VirtualPantry (ingredientID, qtyHave, measureID) VALUES (?, ?, ?)", 
                            (ingredient_id, qty_owned, measure_id,))
        except sql.IntegrityError as e:
            print(f'{e} The Ingredient was ID#: {ingredient_id!r}!')


    # Updates an existing entry
    @staticmethod
    def run_update(ingredient_id: int, qty: str, measure_id: str):
        try:
            with get_connection() as con:
                cur = con.cursor()
                cur.execute('UPDATE VirtualPantry ' \
                            'SET qtyHave = ?, measureID = ? ' \
                            'WHERE ingredientID = ?;',
                            (qty, measure_id, ingredient_id))
                print(f"Adding {ingredient_id} {qty} {measure_id}")
        except sql.IntegrityError as e:
            print(f'{e}: There was an invalid ID given for measure {measure_id!r}. Please check!')


class MeasureTypeQuery(SelectDB):

    select_query = 'SELECT * ' \
                   'FROM MeasureType '
    accepted_filters = {'name': 'name','id': 'measureID'}
    accepted_sorts = {'name': 'name', 'date': 'measureID'}

class SimpleMealQuery(SelectDB):

    select_query = 'SELECT mealID, name, tag, description ' \
                   'FROM Meal '
    accepted_filters = {'name': 'name', 'id': 'id', 'tag': 'tag'}
    accepted_sorts = {'name': 'name', 'id': 'id', 'tag': 'tag'}


class DetailedMealQuery(SelectDB):

    select_query = 'SELECT m.mealID, m.name, m.tag, m.picture, m.description, m.recipe, ' \
                   'mi.ingredientID, i.name, i.tag, i.measureID, mti.name, ' \
                   'mi.qty, mi.measureID, mtm.name ' \
                   'FROM Meal as m '\
                   'LEFT JOIN MealIngredient as mi '\
                       'on mi.mealID = m.mealID '\
                   'LEFT JOIN Ingredient as i '\
                       'ON i.ingredientID = mi.ingredientID '\
                   'LEFT JOIN MeasureType as mtm '\
                       'ON mtm.measureID = mi.measureID '\
                   'LEFT JOIN MeasureType as mti '\
                       'ON mti.measureID = i.measureID '
    accepted_filters = {'name' : 'm.name', 'id': 'm.mealID', 'tag': 'm.tag'}
    accepted_sorts = {'name' : 'm.name', 'date': 'm.mealID', 'tag': 'm.tag'}

    delete_table_name = 'Meal'
    delete_id_name = 'mealID'

    @staticmethod
    def run_insert(name: str, 
                   tag: str | None = None, 
                   picture: str | None = None, 
                   description: str | None = None, 
                   recipe : str | None = None
                   ) -> int:
        with get_connection() as con:
            cur = con.cursor()
            cur.execute('INSERT INTO Meal(name, tag, picture, description, recipe) VALUES (?, ?, ?, ?, ?);', 
                        (name, tag, picture, description, recipe))
            meal_id = cur.lastrowid
            if meal_id is None:
                raise ValueError('Insert into Meal did not give a row ID')
            return meal_id
        
    @staticmethod
    def run_update(meal_id: int,
                   name: str,
                   tag: str | None = None, 
                   picture: str | None = None, 
                   description: str | None = None, 
                   recipe : str | None = None):
        with get_connection() as con:
            cur = con.cursor()
            cur.execute('UPDATE Meal SET name = ?, tag = ?, picture = ?, description = ?, recipe = ? WHERE mealID = ? ;',
                        (name, tag, picture, description, recipe, meal_id))


class MealIngredientsQuery():
    @staticmethod
    def run_update(meal_id: int,
                   ingredients: dict):
        """ingredients: {ing_id: (qty, measure_id)}"""
        with get_connection() as con:
            cur = con.cursor()
            rows = cur.execute('SELECT ingredientID FROM MealIngredient WHERE mealID = ?', (meal_id,)).fetchall()
            existing_ing = {r[0] for r in rows}  # This gives a set of unique ing_id

            removed = existing_ing - ingredients.keys()  # Gives us the difference of ids (thanks discrete math)

            # Removes missing ingredients (They were removed by user)
            if removed is not None:
                cur.executemany('DELETE FROM MealIngredient WHERE mealID = ? AND ingredientID = ?', [(meal_id, ing_id) for ing_id in removed],)

            # Inserts new and updates old
            cur.executemany(
                'INSERT INTO MealIngredient (mealID, ingredientID, qty, measureID) ' \
                'VALUES (?,?,?,?) ' \
                'ON CONFLICT (mealID, ingredientID) ' \
                'DO UPDATE SET qty = excluded.qty, measureID = excluded.measureID ',
                [(meal_id, ing_id, qty, measure_id) for ing_id, (qty, measure_id) in ingredients.items()]
            )
