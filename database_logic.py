# Purpose: Get data to and from the database.
import sqlite3 as sql
from scripts.database_tools import BaseDB


type Name = str
type Tag = str

# This class covers all requests that the Ingredient screen will make
class IngredientLogic(BaseDB):

    query = 'SELECT i.name, t.name ' \
                  'FROM Ingredient as i ' \
                  'LEFT JOIN Tag as t ' \
                      'ON i.tagID = t.tagID '
    accepted_filters = {'ingredient': 'i.name', 'tag': 't.name'}
    accepted_sorts = {'ingredient': 'i.name', 'tag': 't.name'}
    

type Quantity = int
type Ingredient = str
type Abbreviation = str

# This class covers all requests that the Virtual Pantry screen will make
class VirtualPantry(BaseDB):
    
    query = 'SELECT i.name, vp.qtyHave, mt.Abbreviation ' \
                  'FROM VirtualPantry as vp ' \
                  'JOIN MeasureType as mt ' \
                      'ON vp.measureID = mt.measureID ' \
                  'JOIN Ingredient as i ' \
                      'ON vp.ingredientID = i.ingredientID '
    accepted_filters = {'ingredient': 'i.name'}
    accepted_sorts = {'ingredient': 'i.name'}

    
