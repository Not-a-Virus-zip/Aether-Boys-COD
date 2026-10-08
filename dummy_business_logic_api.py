import random

type Quantity = str
type Ingredient = str

class BusinessLogic:
    def load_virtual_pantry_contents(self) -> list[tuple[Ingredient, Quantity]]:
        """Code to generate dummy data for developing the Virtual Pantry UI"""
        example_ingredients = [f"Test Ingredient {i}" for i in range(20)]
        test_units = ["lbs", "gal", "oz", "pkgs"]
        return [
            (ingr, f"{random.randint(2, 60)} {random.choice(test_units)}")
            for i, ingr in enumerate(example_ingredients, start=1)
        ]

    def load_ingredient_list(self) -> list[Ingredient]:
        """Code to generate dummy ingredients"""
        return [f"Test Ingredient {i}" for i in range(20)]