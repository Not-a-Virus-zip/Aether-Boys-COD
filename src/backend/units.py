import pint

units: pint.UnitRegistry = pint.UnitRegistry()


def get_units(unit_name: str) -> pint.Unit:
    try:
        return getattr(units, unit_name)
    except pint.UndefinedUnitError:
        units.define("")