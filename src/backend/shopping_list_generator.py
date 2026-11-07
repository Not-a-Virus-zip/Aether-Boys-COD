from dataclasses import dataclass
from datetime import date

from . import (
    ingredient_list as il,
    virtual_pantry as vp,
    units as u,
)
from src.database.database_logic import (
    ShoppingListQuery as shop_query,
)
import pint

@dataclass(frozen=True)
class ShoppingList:
    # note: the "..." syntax is how you say that a tuple has any number of values of one specific type
    ingredients_needed: tuple[tuple[il.ExistingIngredient, pint.Quantity], ...] 

class ShoppingListGenerator:
    def __init__(self, virtual_pantry: vp.VirtualPantry) -> None:
        self.virtual_pantry = virtual_pantry

    def get_needed_ingredients(self, start_date: date, end_date: date) -> ShoppingList:
        """Gets a list of ingredients in range of dates"""
        needed = (
            (il.ExistingIngredient(name, '', u.MeasureType(measure_id, measure_name), ing_id), qty) 
            for ing_id, name, qty, measure_id, measure_name
            in shop_query.run_select_needed_ingredients(start_date.isoformat(), end_date.isoformat())
        )
        ingredient_dict: dict[il.ExistingIngredient, pint.Quantity] = {}
        for ingr, qty in needed:
            qty = qty * ingr.measurement_type.pint_unit
            if ingr in ingredient_dict:
                ingredient_dict[ingr] += qty
            else:
                ingredient_dict[ingr] = qty
        
        return ShoppingList(tuple(ingredient_dict.items()))