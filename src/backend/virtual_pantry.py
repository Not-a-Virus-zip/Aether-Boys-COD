import pint

from . import (
    ingredient_list as il,
    units,
)
from ..db_scripts import database_logic as db


class VirtualPantry:
    current_contents: list[tuple[il.ExistingIngredient, pint.Quantity]] | None
    # current_contents: dict[il.ExistingIngredient, pint.Quantity]
    # You can add parameters to the constructor if needed
    # (like if it needs to be passed some sort of DatabaseController class or anything else)
    def __init__(self) -> None:
        pass

    def update_vpantry_entry(self, updated_ingr: il.ExistingIngredient, new_quant: pint.Quantity):
        """Update the ingredient quantity stored in the virtual pantry, replacing the previous quantity (if one existed)"""
        raise NotImplementedError

    def load_virtual_pantry_contents(self) -> list[tuple[il.ExistingIngredient, pint.Quantity]]:
        """Get the current contents of the virtual pantry"""
        contents = []
        for ing_id, name, qty, ing_units in db.VirtualPantryQuery.run_select():
            ingr = il.ExistingIngredient(name, "", units.get_units(ing_units), ing_id)
            quantity = qty * ingr.measurement_type
            contents.append((ingr, quantity))
        return contents

