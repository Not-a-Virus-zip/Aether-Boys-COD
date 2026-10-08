

type Quantity = str
type Ingredient = str

class BusinessLogic:
    def load_virtual_pantry_contents(self) -> list[tuple[Ingredient, Quantity]]:
        ...