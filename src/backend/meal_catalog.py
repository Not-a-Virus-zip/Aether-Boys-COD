from __future__ import annotations
from dataclasses import dataclass
import dataclasses

import pint

from . import (
    ingredient_list as il,
    existing,
)

from ..db_scripts import (
    database_logic as db
)

# data passed back from the front-end will be come in instances of this class
@dataclass(frozen=True)
class Meal:
    name: str
    tag: str
    picture: None # TODO: Figure out picture handling
    description: str
    recipe: str
    ingredients: list[tuple[il.ExistingIngredient, pint.Quantity]]

    # this is a method btw
    modify = dataclasses.replace

# when connecting the database to the backend, put data from the database into this class
@dataclass(frozen=True)
class ExistingMeal(Meal):
    id: int

    # this is a method btw
    modify = existing.modify

class MealCatalog:
    def get_meals(self) -> list[ExistingMeal]:
        unprocessed_meals = db.MealQuery.run_select()
        # Please figure out how to do this. I have no idea

        return []