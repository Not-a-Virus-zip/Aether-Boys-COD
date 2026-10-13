from dataclasses import dataclass

import pint


@dataclass(frozen=True)
class Ingredient:
    name: str
    tag: str
    measurement_type: pint.Unit

    def modify(self, name: str | None = None, tag: str | None = None, measurement_type: pint.Unit | None = None):
        return Ingredient(name if name is not None else self.name)



class IngredientList:

    # API used by the UI code for the ingredient list screen

    # TODO: Replace "raise NotImplementedError" with actual implementation

    def update_ingredient(self, updated_ingredient: Ingredient):
        raise NotImplementedError

    def search_ingredient_tags(self, query: str) -> list[str]:
        """Search for existing ingredient tags"""
        raise NotImplementedError

    def search_ingredient_units(self, query: str) -> list[pint.Unit]:
        """Search for possible ingredient units"""
        raise NotImplementedError

    def load_ingredient_list(self) -> list[Ingredient]:
        """Code to generate dummy ingredients"""
        raise NotImplementedError