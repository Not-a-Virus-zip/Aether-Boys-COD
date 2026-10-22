from __future__ import annotations
import pint

from . import (
    ingredient_list as il,
    units,
)
from ..db_scripts import database_logic as db


def into_measure_type_id(unit) -> int:
    unit_name = str(unit)
    if unit_name == "dimensionless":
        unit_name = "piece" # TODO: Replace this stuff with better implementation
    results = db.MeasureTypeQuery.run_select(filter_column="name", filter_value=unit_name, exact=True)
    if not results: raise ValueError("no unit found")
    print(f"{results = }")
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
    def __init__(self) -> None:
        pass

    def update_vpantry_entry(self, updated_ingr: il.ExistingIngredient, new_quant: pint.Quantity):
        """Update the ingredient quantity stored in the virtual pantry, replacing the previous quantity (if one existed)"""
        db.VirtualPantryQuery.run_update(str(updated_ingr.id), new_quant.magnitude, into_measure_type_id(new_quant.units))

    def add_vpantry_entry(self, updated_ingr: il.ExistingIngredient, new_quant: pint.Quantity):
        """Update the ingredient quantity stored in the virtual pantry, replacing the previous quantity (if one existed)"""
        db.VirtualPantryQuery.run_insert(str(updated_ingr.id), new_quant.magnitude, into_measure_type_id(new_quant.units))

    def load_virtual_pantry_contents(self) -> list[tuple[il.ExistingIngredient, pint.Quantity]]:
        """Get the current contents of the virtual pantry"""
        contents = []
        for ing_id, name, qty, ms_id, ms_name, ms_abbrev in db.VirtualPantryQuery.run_select():
            ingr = il.ExistingIngredient(name, "", units.MeasureType(ms_id, ms_name), ing_id)
            quantity = qty * units.get_units(ms_name)
            contents.append((ingr, quantity))
        return contents

