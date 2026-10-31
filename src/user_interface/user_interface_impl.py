from __future__ import annotations

# Standard Library Imports
from typing import Any, Callable, Iterable
from tkinter import messagebox, ttk
import tkinter as tk
from dataclasses import dataclass

# External Library Imports
import pint

# Meal Planner Imports
from . import (
    edit_menu as em,
    virtual_pantry as vp,
    ingredients_list as il,
    meal_catalog as mc,
    calendar as cal,
)
from ..backend import (
    ingredient_list as il_backend,
    virtual_pantry as vp_backend,
    meal_catalog as mc_backend,
)


def fmt_qty(qty: pint.Quantity | pint.Unit) -> str:
    return f"{qty:~P}"

placeholder_image: tk.PhotoImage

def launch_ui():
    app = Application()
    global placeholder_image
    placeholder_image = tk.PhotoImage(file="assets/placeholder.png")
    app.run()

@dataclass
class Backend:
    """Collection of the various backend classes for ease of distribution"""
    ingredients: il_backend.IngredientList
    pantry: vp_backend.VirtualPantry
    meals: mc_backend.MealCatalog

class Application:
    """The class that runs the application and handles any setup for the backend and database."""
    root: tk.Tk
    interface: UserInterface
    backend: Backend

    def __init__(self):
        self.root = tk.Tk()
        self.root.wm_title("Meal Planner")
        self.root.geometry("550x400")
        self.backend = Backend(
            il_backend.IngredientList(),
            vp_backend.VirtualPantry(),
            mc_backend.MealCatalog(),
        )
        self.interface = UserInterface(self.root, self.backend)

    def run(self):
        self.root.mainloop()

class UserInterface:
    pantry: vp.VirtualPantry
    meals: mc.MealCatalog
    calendar: cal.Calendar
    shopping_list: DummyInterface
    ingredients: il.IngredientsList
    settings: DummyInterface

    def __init__(self, root: tk.Tk, backend: Backend):
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        top_bar_menu = ttk.Notebook(root, name="top_bar_menu")

        self.pantry = vp.VirtualPantry(top_bar_menu, backend)
        self.meals = mc.MealCatalog(top_bar_menu, backend)
        self.calendar = cal.Calendar(top_bar_menu, backend)
        self.shopping_list = DummyInterface("Your Shopping List", ttk.Frame(top_bar_menu, name="shopping"))
        self.ingredients = il.IngredientsList(top_bar_menu, self.pantry, backend.ingredients)
        self.settings = DummyInterface("Settings", ttk.Frame(top_bar_menu, name="settings"))

        self.contents = (
            self.pantry,
            self.meals,
            self.calendar,
            self.shopping_list,
            self.ingredients,
            self.settings,
        )

        # register each ui section with the notebook
        for thing in self.contents:
            top_bar_menu.add(
                thing.frame,
                text=thing.name,
                state=tk.DISABLED if isinstance(thing, DummyInterface) else tk.NORMAL
            )

        top_bar_menu.select(self.ingredients.frame)
        top_bar_menu.grid(row=0, column=0, sticky="nsew")

def make_buttons(put_in: tk.Misc, button_instructions: Iterable[tuple[str, Callable[[], None]] | str | int], button_weight: int | None = None) -> tuple[ttk.Frame, list[ttk.Button]]:
    """Helper function used to create buttons at the bottom of a page"""
    bottom_buttons_frame = ttk.Frame(put_in)
    buttons = []

    def generate_button(name: str, command=None):
        button = ttk.Button(bottom_buttons_frame, text=name)
        if command is not None:
            button.config(command=command)
        if button_weight is not None and button_weight > 0:
            bottom_buttons_frame.columnconfigure(i, weight=button_weight, uniform="button")
            button.grid(row=0, column=i, sticky="ew")
        else:
            button.grid(row=0, column=i)
        buttons.append(button)

    for i, slot in enumerate(button_instructions):
        match slot:
            case str(name):
                generate_button(name)
            case str(name), command:
                generate_button(name, command)
            case int(weight):
                bottom_buttons_frame.columnconfigure(i, weight=weight)
    return bottom_buttons_frame, buttons

@dataclass
class DummyInterface:
    """Placeholder for unimplemented parts of the UI"""
    name: str
    frame: ttk.Frame

