from __future__ import annotations

import pint

from . import (
    ingredient_list as il,
    units,
    backend_tools as bt,
)
from ..database import (
    database_logic as db,
    database_tools as dt,
)
from ..user_interface import user_interface_impl as ui
from ..update_flags import DataUpdate


def into_measure_type_id(unit) -> int:
    unit_name = str(unit)
    if unit_name == "dimensionless":
        unit_name = "piece" # TODO: Replace this stuff with better implementation
    results = db.MeasureTypeQuery.run_select(filter_column="name", filter_value=unit_name, exact=True)
    if not results: raise ValueError("no unit found")
    return int(results[0][0])

def into_measure_type(unit) -> units.MeasureType:
    unit_name = str(unit)
    if unit_name == "dimensionless":
        unit_name = "piece" # TODO: Replace this stuff with better implementation
    results = db.MeasureTypeQuery.run_select(filter_column="name", filter_value=unit_name, exact=True)
    if not results: raise ValueError("no unit found")
    print(f"{results = }")
    return units.MeasureType(int(results[0][0]), str(results[0][1]))


class VirtualPantry:
    current_contents: list[tuple[il.ExistingIngredient, pint.Quantity]] | None
    # current_contents: dict[il.ExistingIngredient, pint.Quantity]
    # You can add parameters to the constructor if needed
    # (like if it needs to be passed some sort of DatabaseController class or anything else)
    def __init__(self, app: ui.Application) -> None:
        self.app = app

    def broadcast_changes_to_ui(self):
        self.app.handle_update(DataUpdate.VirtualPantry)

    def update_vpantry_entry(self, updated_ingr: il.ExistingIngredient, new_quant: pint.Quantity):
        """Update the ingredient quantity stored in the virtual pantry, replacing the previous quantity (if one existed)"""
        db.VirtualPantryQuery.run_update(updated_ingr.id, new_quant.magnitude, str(into_measure_type_id(new_quant.units)))
        self.broadcast_changes_to_ui()

    def add_vpantry_entry(self, updated_ingr: il.ExistingIngredient, new_quant: pint.Quantity):
        """Update the ingredient quantity stored in the virtual pantry, replacing the previous quantity (if one existed)"""
        db.VirtualPantryQuery.run_insert(updated_ingr.id, new_quant.magnitude, str(into_measure_type_id(new_quant.units)))
        self.broadcast_changes_to_ui()

    def load_virtual_pantry_contents(self) -> list[tuple[il.ExistingIngredient, pint.Quantity]]:
        """Get the current contents of the virtual pantry"""
        contents = []
        for ing_id, name, qty, ms_id, ms_name, ms_abbrev in db.VirtualPantryQuery.run_select():
            ingr = il.ExistingIngredient(name, "", units.MeasureType(ms_id, ms_name), ing_id)
            quantity = qty * units.get_units(ms_name)
            contents.append((ingr, quantity))
        return contents

    def delete_vpantry_entry(self, ingredient_id: int):
        """Deletes an ingredient from the VP, no restrictions"""
        db.VirtualPantryQuery.run_delete(ingredient_id)
        self.broadcast_changes_to_ui()

    def add_purchased_ingredients(self, bought_ingredients: tuple[tuple[il.ExistingIngredient, pint.Quantity], ...]):
        measure_ids = dt.load_measure_ids()
        
        # Get current Virtual Pantry
        curr_vp = {ing_id: units.unit_reg.Quantity(qty, unit) for ing_id, qty, unit in db.VirtualPantryQuery.run_select_backend()}

        # List of ingredients to be added
        to_update = []

        # Make a list of ingredients that need to have quantity updated / Ingredients that need to be added
        for ing,qty in bought_ingredients:
            if ing.id in curr_vp:
                qty = curr_vp[ing.id] + qty
            to_update.append((ing.id, qty.m, bt.pint_to_measure_ids(measure_ids, qty)))

        db.VirtualPantryQuery.run_bulk_insert_update(tuple(to_update))

        self.broadcast_changes_to_ui()

