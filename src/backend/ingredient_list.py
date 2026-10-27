from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from ..database.database_logic import (
    IngredientQuery as iq,
    MeasureTypeQuery as mq,
)
from ..errors import (
    QueryDeleteError,
    IngredientInUseError,
)
from .units import MeasureType
from . import (
    existing,
    backend_tools as bt,
)


# Note construct like so:
#   Ingredient(5, "example name", "example tag", units.kilogram)
# `@dataclass` automatically generates a constructor using the type annotations
@dataclass(frozen=True)
class Ingredient:
    # feel free to add more fields if needed
    name: str
    tag: str
    measurement_type: MeasureType  # pint.Unit - Right now the MeasurementType database doesn't use Pint. Will change after demo

    # this is a method btw
    modify = dataclasses.replace
    __post_init__ = existing.type_check_self


@dataclass(frozen=True)
class ExistingIngredient(Ingredient):
    """An ingredient with an id that currently exists in the database"""
    # feel free to add more fields if needed
    id: int

    # this is a method btw
    modify = existing.modify
    __post_init__ = existing.type_check_self


def ingredient_from_db_tuple(db_tuple: tuple[int, str, str | None, int, str]) -> ExistingIngredient:
    """Logic for constructing an ExistingIngredient from database information"""
    id, name, tag, measure_id, measure_name = db_tuple
    
    measure = MeasureType(measure_id, measure_name)
    if tag is None:
        tag = ''  # If tk tries to show None, it blows up :D
    return ExistingIngredient(name, bt.denull(tag), measure, id)


class IngredientList:
    # You can add arguments to the constructor if needed
    # (like if it needs to be passed some sort of DatabaseController class or anything else)
    def __init__(self) -> None:
        pass

    # API used by the UI code for the ingredient list screen

    # TODO: Replace "raise NotImplementedError" with actual implementation

    def update_ingredient(self, modified: ExistingIngredient):
        """Store a modified version of an ingredient, replacing the previous version"""
        # if f'{modified.tag}'.strip() == '':
        #     modified = modified.modify(tag = None)
        iq.run_update(modified.id, modified.name, bt.renull(modified.tag), modified.measurement_type.id)

    def create_ingredient(self, name: str, tag: str, measure_type: int):
        """Create a new ingredient"""
        # if f'{tag}'.strip() == '':
        #     tag = None
        iq.run_insert(name, bt.renull(tag)  , measure_type)

    # Pulls up a list of available MeasurementTypes(?)
    def search_ingredient_units(self, query: str) -> list[str]:  #TODO: list[pint.Unit] 
        """Search for possible ingredient units"""
        return [str(name) for _, name, *_ in mq.run_select(filter_column="name", filter_value=query)]

    def load_ingredient_list(self,
                             filter_column: str | None = None, 
                             filter_value: str | None = None,
                             sort_mode: str | None = None,
                             asc: bool = True,
                             ) -> list[ExistingIngredient]:
        """Get the current ingredient list"""
        raw_ingredients = iq.run_select(filter_column=filter_column, filter_value=filter_value, order=sort_mode, asc=asc)
        return [ingredient_from_db_tuple(db_tuple) for db_tuple in raw_ingredients]

    def tags_in_use(self, query: str):
        """Get a list of unique tags in use"""
        return [tag for tag, in iq.run_get_tags(query or None)]

    def delete_ingredient(self, ingredient_id: int):
        """Remove an ingredient from the database, restricted by Meal"""
        try:
            iq.run_delete(ingredient_id)   
        except QueryDeleteError as e:
            raise IngredientInUseError from e  # This error gets raised if the ingredient is part of a meal. If it is in virtual pantry it will get silently deleted. Make sure to give warnings.