import random
import pint

units = pint.UnitRegistry()
units.define("package = [generic_container_unit] = pkg")
type Quantity = pint.Quantity
type Ingredient = str

class BusinessLogic:
    def __init__(self) -> None:
        self.test_ingredients = [f"Test Ingredient {i}" for i in range(20)]
        
        test_units = [units.pound, units.gallon, units.ounce, units.package]
        self.test_virtual_pantry = [
            (ingr, random.randint(2, 60) * random.choice(test_units))
            for ingr in self.test_ingredients
        ]

    def load_virtual_pantry_contents(self) -> list[tuple[Ingredient, Quantity]]:
        """Return dummy data for developing the Virtual Pantry UI"""
        return self.test_virtual_pantry

    def load_ingredient_list(self) -> list[Ingredient]:
        """Code to generate dummy ingredients"""
        return self.test_ingredients

    def update_ingredient(self, updated_ingredient: Ingredient):
        pass

    def update_vpantry_entry(self, updated_ingr: Ingredient, new_quant: Quantity):
        """Dummy Implementation"""
        for i, (ingr, _) in enumerate(self.test_virtual_pantry):
            if ingr == updated_ingr:
                self.test_virtual_pantry[i] = updated_ingr, new_quant