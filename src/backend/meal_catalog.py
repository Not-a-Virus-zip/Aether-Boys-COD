from __future__ import annotations
from dataclasses import dataclass, asdict
import dataclasses
from re import search

import pint

from . import (
    ingredient_list as il,
    existing,
    units,
    backend_tools as bt,
)

from ..database import (
    database_logic as db,
    database_tools as dt,
)


# Currently only used as a base class for DetailedMeal and ExistingDetailedMeal
@dataclass(frozen=True)
class SimpleMeal:
    name: str
    tag: str
    description: str

    # this is a method btw
    modify = existing.modify

    # adds runtime type-checks to instances of this class (and all subclasses)
    __post_init__ = existing.type_check_self

# data passed back from the front-end will be come in instances of this class
@dataclass(frozen=True)
class DetailedMeal(SimpleMeal):
    picture: str # TODO: Figure out picture handling
    recipe: str
    ingredients: tuple[tuple[il.ExistingIngredient, pint.Quantity], ...]

# when connecting the database to the backend, put data from the database into this class
@dataclass(frozen=True)
class ExistingSimpleMeal(SimpleMeal):
    id: int

@dataclass(frozen=True)
class ExistingDetailedMeal(DetailedMeal):
    id: int

class NeverUse:
    pass

def unit_test_typechecking():
    correct_values = ExistingDetailedMeal("", "kjhgfd", "fdsg", "dskfgjh", "jhdflgk", (), 5)
    fields = dataclasses.fields(ExistingDetailedMeal)
    for field in fields:
        try:
            correct_values.modify(**{field.name: NeverUse()})
        except TypeError as err:
            pass # test pass
            continue
        except NameError as err:
            continue
        raise Exception(f"Failed to catch type error on field: {field}")



class MealCatalog:
    def get_simple_meals(self, sort_column: str = "name", asc: bool = True, search_term: str = "") -> list[ExistingSimpleMeal]:
        filter_value = search_term or None # if search_term is blank, filter value is None
        filter_column = filter_value and "name" # if filter value is not None, filter column is name
        return [
            ExistingSimpleMeal(name, bt.denull(tag), bt.denull(description), id)
            for id, name, tag, description in db.SimpleMealQuery.run_select(order=sort_column, asc=asc, filter_column=filter_column, filter_value=filter_value)
        ]

    def get_simple_meal(self, meal_id: int) -> ExistingSimpleMeal:
        result = db.SimpleMealQuery.run_select(filter_column="id", filter_value=str(meal_id), exact=True)
        match result:
            case []:
                raise ValueError(f"Unknown id: {meal_id}")
            case [(id, name, tag, description)]:
                return ExistingSimpleMeal(name, bt.denull(tag), bt.denull(description), id)
            case more_than_one:
                raise Exception(f"Found more than one meal ({len(more_than_one)}) with id = {meal_id}. (??)")

    def get_detailed_meal(self, meal_id: int) -> ExistingDetailedMeal:
        meal_ingredients = db.DetailedMealQuery.run_select(filter_column='id', filter_value=str(meal_id), exact=True)
        ingredients = []
        meal = ExistingSimpleMeal(meal_ingredients[0][1], bt.denull(meal_ingredients[0][2]), bt.denull(meal_ingredients[0][4]), meal_ingredients[0][0])
        picture, recipe = meal_ingredients[0][3], meal_ingredients[0][5]
        if meal_ingredients[0][6] is not None:
            for ingredient in meal_ingredients:
                ing_id, ing_name, ing_tag, ing_measure_id, ing_measure_name = ingredient[6:11]  # Ingredient Information
                mi_qty, mi_measure_id, mi_measure_name = ingredient[11:14]  # MealIngredient Information

                ing = il.ExistingIngredient(ing_name, bt.denull(ing_tag), units.MeasureType(ing_measure_id, ing_measure_name), ing_id)
                ingredients.append((ing, units.units.Quantity(mi_qty, mi_measure_name)))

        return ExistingDetailedMeal(**asdict(meal), picture=bt.denull(picture), recipe=bt.denull(recipe), ingredients=tuple(ingredients))

    def update_meal(self, modified: ExistingDetailedMeal) -> None:
        """This method updates an existing meal"""
        # Ingredient Check
        ingredients = self._get_ing_dict(modified)

        # Update db
        db.DetailedMealQuery.run_update(modified.id, modified.name, bt.renull(modified.tag), bt.renull(modified.picture), 
                                        bt.renull(modified.description), bt.renull(modified.recipe))
        db.MealIngredientsQuery.run_update(modified.id, ingredients)

    def create_meal(self, new_meal: DetailedMeal) -> None:
        """This method creates a new meal"""
        ingredients = self._get_ing_dict(new_meal)

        new_id = db.DetailedMealQuery.run_insert(new_meal.name, bt.renull(new_meal.tag), bt.renull(new_meal.picture), 
                                                 bt.renull(new_meal.description), bt.renull(new_meal.recipe))
        db.MealIngredientsQuery.run_update(new_id, ingredients)

    def _get_ing_dict(self, detailed_meal: DetailedMeal) -> dict:
        measure_ids = dt.load_measure_ids()
        if detailed_meal.ingredients is not None:
            ingredients = {ingredient.id: (measure.magnitude, bt.pint_to_measure_ids(measure_ids, measure)) for ingredient, measure in detailed_meal.ingredients}
        else:
            ingredients = dict()
        return ingredients

    def delete_meal(self, meal_id: int) -> None:
        """Deletes a meal from the database, no restrictions (yet)"""
        db.DetailedMealQuery.run_delete(meal_id)

