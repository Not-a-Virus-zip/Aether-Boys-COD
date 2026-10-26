from __future__ import annotations
from tkinter import ttk
import tkinter as tk

import pint

from . import (
    edit_menu as em,
    user_interface_impl as ui,
)
from .treeview_utilities import ScrollableTreeview, AutoSorter
from ..backend import (
    virtual_pantry as vp_backend,
    ingredient_list as il_backend,
    units
)
from ..backend.ingredient_list import (Ingredient, ExistingIngredient)


class VirtualPantry:
    """Constructs and controls the virtual pantry UI"""
    name: str = "Virtual Pantry"
    
    pantry_backend: vp_backend.VirtualPantry
    ing_backend: il_backend.IngredientList
    frame: ttk.Frame
    pantry_display: ScrollableTreeview
    auto_sorter: AutoSorter
    pantry_contents: list[tuple[ExistingIngredient, pint.Quantity]]
    add_button: ttk.Button
    edit_button: ttk.Button

    def __init__(self, parent: ttk.Notebook, backend: ui.Backend):
        self.pantry_backend = backend.pantry
        self.ing_backend = backend.ingredients
        self.frame = ttk.Frame(parent, name="virtual pantry", padding=20)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.pantry_display = ScrollableTreeview(self.frame, columns=["ingr", "qty"], show="headings", selectmode=tk.BROWSE)
        self.auto_sorter = AutoSorter(self.pantry_display.treeview, self._autosorter_command)
        tv = self.pantry_display.treeview
        tv.heading("ingr", text="Ingredient")
        tv.column("ingr", anchor="w")
        tv.heading("qty", text="Quantity")
        tv.column("qty", anchor="e")

        self.pantry_contents = []
        self.refresh_pantry()
        self.pantry_display.grid(row=0, column=0, sticky="news")
        self.frame.grid(row=0, column=0, sticky="news")
        buttons_frame, (self.add_button, self.edit_button) = \
            ui.make_buttons(self.frame, ("Add New", "Edit Selected"), button_weight=1)
        self.add_button.config(command=self.press_add_button)
        self.edit_button.config(command=self.press_edit_button, state=tk.DISABLED)
        buttons_frame.grid(row=1, column=0, sticky="ew")

        tv.bind("<<TreeviewSelect>>", self._on_selection_change)

    def refresh_pantry(self):
        self.auto_sorter.refresh()

    def _autosorter_command(self, query: str, column: str, asc: bool):
        if len(self.pantry_contents) > 0:
            self.pantry_display.treeview.delete(*range(len(self.pantry_contents)))
        self.pantry_contents = self.pantry_backend.load_virtual_pantry_contents()
        if column == "qty":
            self.pantry_contents.sort(key=lambda t: t[1].magnitude, reverse=not asc)
        elif not asc:
            self.pantry_contents.reverse()
        for i, (ingr, qty) in enumerate(self.pantry_contents):
            self.pantry_display.treeview.insert("", "end", id=i, text="", values=[ingr.name, ui.fmt_qty(qty)])

    def _on_selection_change(self, tv: tk.Event) -> object:
        self.edit_button.config(state=tk.NORMAL if self.is_ingr_selected() else tk.DISABLED)
    
    def is_ingr_selected(self) -> bool:
        return len(self.pantry_display.treeview.selection()) != 0

    def get_selected(self) -> tuple[ExistingIngredient, pint.Quantity] | None:
        selection = self.pantry_display.treeview.selection()
        return None if len(selection) == 0 else self.pantry_contents[int(selection[0])]

    def press_add_button(self):
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Add Ingredient",
            lambda tl: VPantryAddMenu(self, tl).frame
        )

    def press_edit_button(self):
        selection = self.get_selected()
        assert selection is not None, "Edit button should be disabled when nothing is selected"
        name, qty = selection
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Edit Ingredient",
            lambda tl: VPantryEditMenu(self, tl, name, qty).frame
        )

class VPantryEditMenu(em.EditMenu):
    """Constructs and controls the menu for editing an ingredient that's already in the virtual pantry"""
    pantry: VirtualPantry
    container: tk.Toplevel
    ingredient_name: em.MenuField[em.Display]
    amount: em.MenuField[em.QuantityEntry]
    save_button: ttk.Button
    cancel_button: ttk.Button

    def __init__(self, pantry: VirtualPantry, container: tk.Toplevel, ingredient: ExistingIngredient, qty: pint.Quantity) -> None:
        super().__init__(container)
        self.ingredient_name = self.insert("Ingredient", em.Display(self.frame, ingredient.name))
        self.amount          = self.insert("Quantity", em.QuantityEntry(self.frame, qty))
        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])
        self.cancel_button.configure(command=container.destroy)
        self.save_button.configure(command=self.save_and_close)
        self.ingredient = ingredient
        self.prev_quantity = qty
        self.pantry = pantry
        self.container = container

    def save_and_close(self):
        new_quantity = self.amount.elem.get_quantity()
        # TODO: handle this case
        # assert self.prev_quantity.is_compatible_with(new_quantity)
        self.pantry.pantry_backend.update_vpantry_entry(self.ingredient, new_quantity)
        self.pantry.refresh_pantry()
        self.container.destroy()

class VPantryAddMenu(em.EditMenuWithSearcher):
    """
    Constructs and controls the menu for adding a new ingredient to the virtual pantry.
    This uses a different class because it requires selecting what ingredient to add."""
    pantry: VirtualPantry
    container: tk.Toplevel
    ingredient_name: em.MenuField[em.ClosedDbSearchOptions[ExistingIngredient]]
    amount: em.MenuField[em.QuantityEntry]
    save_button: ttk.Button
    cancel_button: ttk.Button

    last_search: list[ExistingIngredient]

    def __init__(self, pantry: VirtualPantry, container: tk.Toplevel) -> None:
        super().__init__(container)

        self.ingredient_name = self.insert_searcher("Ingredient", em.ClosedDbSearchOptions(self.frame, "Ingredients", "Missing Ingredient", self._search, lambda i: i.name))
        self.amount          = self.insert("Quantity", em.QuantityEntry(self.frame, 0 * units.units.dimensionless))
        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])
        self.cancel_button.configure(command=container.destroy)
        self.save_button.configure(command=self.save_and_close)
        self.pantry = pantry
        self.container = container

        self.last_search = []

    def _search(self, query: str) -> list[ExistingIngredient]:
        return self.pantry.ing_backend.load_ingredient_list("name", query)

    def save_and_close(self):
        if not self.check_all_input_and_show_errors():
            return
        new_quantity = self.amount.elem.get_quantity()
        ingredient = self.ingredient_name.elem.get_selection()
        # TODO: handle this case
        assert ingredient is not None
        self.pantry.pantry_backend.add_vpantry_entry(ingredient, new_quantity)
        self.pantry.refresh_pantry()
        self.container.destroy()
