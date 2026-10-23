import pint


def denull(s):
    return "" if s is None else s

def renull(s):
    return None if s == '' else s

def pint_to_measure_ids(measure_ids: dict[str, int], pint_var: pint.Quantity) -> int:
    unit_name = str(pint_var.units)
    try:
        return measure_ids[unit_name]
    except KeyError:
        raise ValueError(f'No MeasureType for this unit {unit_name!r}')
