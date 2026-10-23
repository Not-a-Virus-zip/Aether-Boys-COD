from __future__ import annotations
from dataclasses import dataclass, asdict
import dataclasses
import typing

import pint

from . import (
    ingredient_list as il,
    existing,
    units,
)

from ..db_scripts import (
    database_logic as db
)

# Currently only used as a base class for DetailedMeal and ExistingDetailedMeal
@dataclass(frozen=True)
class SimpleMeal:
    name: str
    tag: str
    description: str

    # this is a method btw
    modify = dataclasses.replace

    # adds runtime type-checks to instances of this class (and all subclasses)
    __post_init__ = existing.type_check_self

# data passed back from the front-end will be come in instances of this class
@dataclass(frozen=True)
class DetailedMeal(SimpleMeal):
    picture: None # TODO: Figure out picture handling
    recipe: str
    ingredients: tuple[tuple[il.ExistingIngredient, pint.Quantity], ...]

# when connecting the database to the backend, put data from the database into this class
@dataclass(frozen=True)
class ExistingSimpleMeal(SimpleMeal):
    id: int

    # this is a method btw
    modify = existing.modify


@dataclass(frozen=True)
class ExistingDetailedMeal(DetailedMeal):
    id: int

    # this is a method btw
    modify = existing.modify


class MealCatalog:
    def get_simple_meals(self) -> list[ExistingSimpleMeal]:
        return [
            ExistingSimpleMeal(name, denull(tag), denull(description), id)
            for id, name, tag, description in db.SimpleMealQuery.run_select()
        ]


    def get_detailed_meal(self, meal_id: int) -> ExistingDetailedMeal:
        meal_ingredients = db.DetailedMealQuery.run_select(filter_column='id', filter_value=str(meal_id), exact=True)
        ingredients = []
        meal = ExistingSimpleMeal(meal_ingredients[0][1], denull(meal_ingredients[0][2]), denull(meal_ingredients[0][4]), meal_ingredients[0][0])
        picture, recipe = meal_ingredients[0][3], meal_ingredients[0][5]
        if meal_ingredients[0][6] is not None:
            for ingredient in meal_ingredients:
                ing_id, ing_name, ing_tag, ing_measure_id, ing_measure_name = ingredient[6:11]  # Ingredient Information
                mi_qty, mi_measure_id, mi_measure_name = ingredient[11:14]  # MealIngredient Information
                ing = il.ExistingIngredient(ing_name, ing_tag, units.MeasureType(ing_measure_id, ing_measure_name), ing_id)
                ingredients.append((ing, units.units.Quantity(mi_qty, mi_measure_name)))
        return ExistingDetailedMeal(**asdict(meal), picture=picture, recipe=denull(recipe), ingredients=tuple(ingredients))


def denull(s):
    return "" if s is None else s