import dataclasses
from dataclasses import dataclass
import pint

# Note construct like so:
#   Ingredient(5, "example name", "example tag", units.kilogram)
# `@dataclass` automatically generates a constructor using the type annotations
@dataclass(frozen=True)
class Ingredient:
    _ingredient_id: int
    # feel free to add more fields if needed
    name: str
    tag: str
    measurement_type: pint.Unit

    def modify(self, **kwargs) -> Ingredient:
        return dataclasses.replace(self, changes=kwargs)

class IngredientList:
    # You can add arguments to the constructor if needed
    # (like if it needs to be passed some sort of DatabaseController class or anything else)
    def __init__(self) -> None:
        raise NotImplementedError

    # API used by the UI code for the ingredient list screen

    # TODO: Replace "raise NotImplementedError" with actual implementation

    def update_ingredient(self, updated_ingredient: Ingredient):
        """Store a modified version of an ingredient, replacing the previous version (if one existed)"""
        raise NotImplementedError

    def search_ingredient_tags(self, query: str) -> list[str]:
        """Search for existing ingredient tags"""
        raise NotImplementedError

    def search_ingredient_units(self, query: str) -> list[pint.Unit]:
        """Search for possible ingredient units"""
        raise NotImplementedError

    def load_ingredient_list(self) -> list[Ingredient]:
        """Get the current ingredient list"""
        raise NotImplementedError