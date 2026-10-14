import dataclasses
from dataclasses import dataclass
import pint
from src.db_scripts.database_logic import IngredientQuery as iq
from ..backend.units import MeasureType

# Note construct like so:
#   Ingredient(5, "example name", "example tag", units.kilogram)
# `@dataclass` automatically generates a constructor using the type annotations
@dataclass(frozen=True)
class Ingredient:
    # feel free to add more fields if needed
    name: str
    tag: str
    measurement_type: str  # pint.Unit - Right now the MeasurementType database doesn't use Pint. Will change after demo

    def modify(self, **kwargs) -> Ingredient:
        return dataclasses.replace(self, changes=kwargs)

@dataclass(frozen=True)
class ExistingIngredient(Ingredient):
    """An ingredient with an id that currently exists in the database"""
    # feel free to add more fields if needed
    id: int

    def modify(self, **kwargs) -> ExistingIngredient:
        assert "id" not in kwargs, "Cannot modify id of existing ingredient"
        return dataclasses.replace(self, changes=kwargs)


class IngredientList:
    # You can add arguments to the constructor if needed
    # (like if it needs to be passed some sort of DatabaseController class or anything else)
    def __init__(self) -> None:
        pass

    # API used by the UI code for the ingredient list screen

    # TODO: Replace "raise NotImplementedError" with actual implementation

    def update_ingredient(self, id: int, name: str, tag: str, measure_type: MeasureType) -> bool:
        """Store a modified version of an ingredient, replacing the previous version (if one existed)"""
        # if check_tag(updated_ingredient.tag) is None:
        #    raise ValueError
        # if check_measuretype(updated_ingredient.measurment_type) is None:
        #    raise ValueError
        return iq.run_update(id, name, tag, measure_type.id)

    def create_ingredient(self, name: str, tag: str, measure_type: MeasureType):
        """Create a new ingredient"""
        iq.run_insert(name, tag, measure_type.id)

    # Pulls up a list of available MeasurementTypes(?)
    def search_ingredient_units(self, query: str) -> list[str]:  #TODO: list[pint.Unit] 
        """Search for possible ingredient units"""
        raise NotImplementedError

    def load_ingredient_list(self, 
                             filter_column: str | None = None, 
                             filter_value: str | None = None
                             ) -> list[ExistingIngredient]:
        """Get the current ingredient list"""
        ing_list = []
        for id, name, tag, measure in iq.run_select(filter_column=filter_column, filter_value=filter_value):
            ing_list.append(ExistingIngredient(name, tag, measure, id))
        return ing_list

# Removed for hello world project
# @dataclass
# class Tag:
#     id: int
#     name: str

# class TagList:
    # Needs update
    # def load_meal_tag_list(self):
    #     """Search for existing meal tags"""
    #     tag_list = []
    #     for tag in tq.run_select(filter_column='type', filter_value='Meal'):
    #         tag_list.append(Tag(tag[0], tag[1]))
    #     return tag_list
    
    # def create_tag(self, name: str, type: str):
    #     """Creates a new tag"""
    #     if type.capitalize().strip() == 'Meal' or type.capitalize().strip() == 'Ingredient':
    #         tq.run_insert(name, type)
    #         new_tag = self.load_ingredient_tag_list()
    #         return new_tag
    #     else:
    #         raise 'type must be \'Ingredient\' or \'Meal\''