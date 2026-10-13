#!/.venv/bin/python

from src.backend import virtual_pantry as vp

test_vpantry = vp.VirtualPantry()
test_vpantry.load_virtual_pantry_contents()