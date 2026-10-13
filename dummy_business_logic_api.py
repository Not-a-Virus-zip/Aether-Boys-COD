import random
import pint
import dataclasses

units = pint.UnitRegistry()
units.define("package = [generic_container_unit] = pkg")

type Quantity = pint.Quantity
type Ingredient = DummyIngredient

@dataclasses.dataclass
class DummyIngredient:
    name: str
    tag: str
    measurement_type: pint.Unit

class BusinessLogic:
    def __init__(self) -> None:
        self.test_tags = [f"{c} Tag" for c in "ABCDEFG"]
        self.test_units = [units.pound, units.gallon, units.ounce, units.package]
        self.test_ingredients = [
            DummyIngredient(f"Test Ingredient {i}", random.choice(self.test_tags), random.choice(self.test_units))
            for i in range(20)
        ]
        
        self.test_virtual_pantry = [
            (ingr, random.randint(2, 60) * ingr.measurement_type)
            for ingr in self.test_ingredients
        ]

    def load_virtual_pantry_contents(self) -> list[tuple[Ingredient, Quantity]]:
        """Return dummy data for developing the Virtual Pantry UI"""
        return self.test_virtual_pantry

    def load_ingredient_list(self) -> list[Ingredient]:
        """Code to generate dummy ingredients"""
        return self.test_ingredients

    def search_tags(self, query: str):
        """testing only"""
        return sorted((tag for tag in self.test_tags if query in tag), key=lambda elem: abs(len(query) - len(elem)))

    def search_units(self, query: str):
        """testing only"""
        return sorted((tag for tag in self.test_units if query in str(tag)), key=lambda elem: abs(len(query) - len(str(elem))))

    def update_ingredient(self, updated_ingredient: Ingredient):
        pass

    def update_vpantry_entry(self, updated_ingr: Ingredient, new_quant: Quantity):
        """Dummy Implementation"""
        for i, (ingr, _) in enumerate(self.test_virtual_pantry):
            if ingr == updated_ingr:
                self.test_virtual_pantry[i] = updated_ingr, new_quant