from __future__ import annotations
import pint
from dataclasses import dataclass, field
from ..db_scripts.database_logic import MeasureTypeQuery as mtq
from . import existing
units: pint.UnitRegistry = pint.UnitRegistry()

def interpret_quantity(quantity: str) -> pint.Quantity:
    # try:
    return units.parse_expression(quantity)
    

def get_units(unit_name: str) -> pint.Unit:
    try:
        return getattr(units, unit_name)
    except pint.UndefinedUnitError:
        return units.dimensionless
        # units.define(f"{unit_name} = ")

@dataclass
class MeasureType:
    id: int
    name: str
    
    # Note: this field gets computed by __post_init__. You don't need to pass in a value for it.
    pint_unit: pint.Unit = field(init=False)

    def __post_init__(self):
        self.pint_unit = getattr(units, self.name)
        existing.type_check_self(self)


class MeasureTypeList:
    def load_measure_type_list(self):
        """Search for existing ingredient tags"""
        mt_list = []
        for measure in mtq.run_select():
            mt_list.append(MeasureType(measure[0], measure[1]))
        return mt_list