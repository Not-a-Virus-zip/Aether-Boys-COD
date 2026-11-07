from dataclasses import dataclass
from datetime import date
from . import (
    ingredient_list as il,
    units as u,
)
from src.database.database_logic import (
    ShoppingListQuery as shop_query,
)
import pint

@dataclass(frozen=True)
class ShoppingList:
    ingredients_needed: tuple[tuple[il.ExistingIngredient, pint.Quantity]]

class ShoppingListGenerator():
    def get_needed_ingredients(self, start_date: date, end_date: date):
        """Gets a list of ingredients in range of dates"""
        needed = ((il.ExistingIngredient(name, '', u.MeasureType(measure_id, measure_name), ing_id), qty) 
                  for ing_id, name, qty, measure_id, measure_name in shop_query.run_select_needed_ingredients(start_date.isoformat(), end_date.isoformat())
        )
        

        