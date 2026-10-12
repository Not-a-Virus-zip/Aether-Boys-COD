# Purpose: Get data to and from the database.
import sqlite3 as sql
from .database_tools import SelectDB, get_connection


type Name = str
type Tag = str

# This class covers all requests that the Ingredient screen will make
class IngredientQuery(SelectDB):

    select_query = 'SELECT i.ingredientID, i.name, t.name ' \
                  'FROM Ingredient as i ' \
                  'LEFT JOIN Tag as t ' \
                      'ON i.tagID = t.tagID '
    accepted_filters = {'ingredient': 'i.name', 'tag': 't.name'}
    accepted_sorts = {'ingredient': 'i.name', 'tag': 't.name', 'date': 'i.ingredientID'}


    def insert(ingredient_name, tag_id, measure_id):
        with get_connection() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Ingredient(name, tagID, measureID) VALUES (?, ?, ?)", 
                        (ingredient_name, tag_id, measure_id,))
            
    

type Quantity = int
type Ingredient = str
type Abbreviation = str

# This class covers all requests that the Virtual Pantry screen will make
class VirtualPantryQuery(SelectDB):
    
    select_query = 'SELECT vp.ingredientID, i.name, vp.qtyHave, mt.Abbreviation ' \
                  'FROM VirtualPantry as vp ' \
                  'JOIN MeasureType as mt ' \
                      'ON vp.measureID = mt.measureID ' \
                  'JOIN Ingredient as i ' \
                      'ON vp.ingredientID = i.ingredientID '
    accepted_filters = {'ingredient': 'i.name'}
    accepted_sorts = {'ingredient': 'i.name'}


    def insert(ingredient_id, qty_owned, measure_id):
        with get_connection() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO VirtualPantry (ingredientID, qtyHave, measureID) VALUES (?, ?, ?)", 
                        (ingredient_id, qty_owned, measure_id,))



