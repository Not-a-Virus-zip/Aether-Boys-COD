import pint

from . import ingredient_list as il


class VirtualPantry:
    # You can add parameters to the constructor if needed
    # (like if it needs to be passed some sort of DatabaseController class or anything else)
    def __init__(self) -> None:
        raise NotImplementedError

    def update_vpantry_entry(self, updated_ingr: il.ExistingIngredient, new_quant: pint.Quantity):
        """Update the ingredient quantity stored in the virtual pantry, replacing the previous quantity (if one existed)"""
        raise NotImplementedError

    def load_virtual_pantry_contents(self) -> list[tuple[il.ExistingIngredient, pint.Quantity]]:
        """Get the current contents of the virtual pantry"""
        raise NotImplementedError
