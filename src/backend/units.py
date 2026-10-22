from __future__ import annotations
import pint
from dataclasses import dataclass
from ..db_scripts.database_logic import MeasureTypeQuery as mtq
from . import existing
units: pint.UnitRegistry = pint.UnitRegistry()


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

    __post_init__ = existing.type_check_self

class MeasureTypeList:
    def load_measure_type_list(self):
        """Search for existing ingredient tags"""
        mt_list = []
        for measure in mtq.run_select():
            mt_list.append(MeasureType(measure[0], measure[1]))
        return mt_list