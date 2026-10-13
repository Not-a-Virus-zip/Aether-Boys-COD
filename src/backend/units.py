import pint

units: pint.UnitRegistry = pint.UnitRegistry()


def get_units(unit_name: str) -> pint.Unit:
    try:
        return getattr(units, unit_name)
    except pint.UndefinedUnitError:
        return units.dimensionless
        # units.define(f"{unit_name} = ")