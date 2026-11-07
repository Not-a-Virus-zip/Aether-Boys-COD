from __future__ import annotations
import pint
from dataclasses import dataclass, field
from ..database.database_logic import MeasureTypeQuery as mtq
from . import existing

unit_reg: pint.UnitRegistry = pint.UnitRegistry()

def interpret_quantity(quantity_expression: str, unit_constraint: pint.Unit | None = None) -> pint.Quantity:
    quantity_expression = quantity_expression.strip()
    if quantity_expression:
        quantity = unit_reg.parse_expression(quantity_expression)
        if unit_constraint is None:
            return quantity
        if quantity.unitless:
            quantity *= unit_constraint
        if not quantity.is_compatible_with(unit_constraint):
            raise ValueError(f"Incompatible units: {quantity.units} and {unit_constraint}")
        return quantity
    else:
        raise ValueError("expected quantity expression, found empty string")
    

def get_units(unit_name: str) -> pint.Unit:
    try:
        return getattr(unit_reg, unit_name)
    except pint.UndefinedUnitError:
        return unit_reg.dimensionless
        # units.define(f"{unit_name} = ")

@dataclass
class MeasureType:
    id: int
    name: str
    
    # Note: this field gets computed by __post_init__. You don't need to pass in a value for it.
    pint_unit: pint.Unit = field(init=False)

    def __post_init__(self):
        self.pint_unit = getattr(unit_reg, self.name)
        existing.type_check_self(self)


class MeasureTypeList:
    def load_measure_type_list(self):
        """Search for existing ingredient tags"""
        mt_list = []
        for measure in mtq.run_select():
            mt_list.append(MeasureType(measure[0], measure[1]))
        return mt_list