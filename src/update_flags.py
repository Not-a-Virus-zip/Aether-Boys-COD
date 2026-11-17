from __future__ import annotations

from enum import (
    Flag,
    auto,
)

class DataUpdate(Flag):
    Ingredients     = auto() # Ingredient Database modified
    Calendar        = auto() # Event Database modified
    VirtualPantry   = auto() # Virtual Pantry Database modified
    MealCatalog     = auto() # Meal Database modified
    Nothing         = 0
