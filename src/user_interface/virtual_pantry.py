from __future__ import annotations

from tkinter import messagebox, ttk
import tkinter as tk

import pint

from . import (
    edit_menu as em,
    user_interface_impl as ui,
)
from .treeview_tools import ScrollableTreeview, AutoSorter
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
        self.pantry_display = ScrollableTreeview(self.frame, columns=["ingr", "qty"], show="headings")
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

        buttons_frame, (
            self.delete_button,
            self.add_button,
            self.edit_button
        ) = ui.make_buttons(
            self.frame,
            (
                ("Delete Selected", self.press_delete_button),
                ("Add New", self.press_edit_button),
                ("Edit Selected", self.press_edit_button),
            ),
            button_weight=1
        )
        self.delete_button.config(state=tk.DISABLED)
        self.edit_button.config(state=tk.DISABLED)

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
        num_selected = self.get_num_selected()
        self.delete_button.config(state=tk.NORMAL if num_selected > 0 else tk.DISABLED)
        self.edit_button.config(state=tk.NORMAL if num_selected == 1 else tk.DISABLED)

    def get_num_selected(self) -> int:
        return len(self.pantry_display.treeview.selection())

    def get_selected(self) -> list[tuple[ExistingIngredient, pint.Quantity]]:
        selection = self.pantry_display.treeview.selection()
        return [self.pantry_contents[int(n)] for n in selection]

    def press_delete_button(self):
        deletion_targets = self.get_selected()
        if len(deletion_targets) == 1:
            ingr, qty = deletion_targets[0]
            removal_msg = f"Are you sure you want to remove {ingr.name} ({ui.fmt_qty(qty)}) from your virtual pantry?"
            detail = ""
        else:
            removal_msg = f"Are you sure you want to remove the following ingredients from your virtual pantry?"
            detail = "\n".join(f"{ingr.name} ({ui.fmt_qty(qty)})" for ingr, qty in deletion_targets)
        if messagebox.askokcancel(
            "Confirm Removal",
            removal_msg,
            detail=detail,
            icon=messagebox.WARNING,
            default=messagebox.CANCEL,
            parent=self.frame,
        ):
            for ingr, _ in deletion_targets:
                self.pantry_backend.delete_vpantry_entry(ingr.id)
                self.refresh_pantry()

    def press_add_button(self):
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Add Ingredient",
            lambda tl: VPantryAddMenu(self, tl).frame
        )

    def press_edit_button(self):
        selection = self.get_selected()
        assert len(selection) == 1, "Edit button should be disabled when the selection is not exactly one ingredient"
        name, qty = selection[0]
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
        self.amount          = self.insert("Quantity", em.QuantityEntry(self.frame, qty, ingredient.measurement_type.pint_unit))
        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])
        self.cancel_button.configure(command=container.destroy)
        self.save_button.configure(command=self.save_and_close)
        self.ingredient = ingredient
        self.prev_quantity = qty
        self.pantry = pantry
        self.container = container

    def save_and_close(self):
        if not self.check_all_input_and_show_errors():
            # TODO: Pop-up error?
            return
        new_quantity = self.amount.elem.get_quantity()
        
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

        self.ingredient_name = self.insert_searcher("Ingredient", em.ClosedDbSearchOptions(self.frame, "Ingredients", "Missing Ingredient", self._search, lambda i: i.name, selection_callback=self._on_ingredient_change))
        self.amount          = self.insert("Quantity", em.QuantityEntry(self.frame, 0 * units.unit_reg.dimensionless, None))
        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])
        self.cancel_button.configure(command=container.destroy)
        self.save_button.configure(command=self.save_and_close)
        self.pantry = pantry
        self.container = container

        self.last_search = []

    def _search(self, query: str) -> list[ExistingIngredient]:
        return self.pantry.ing_backend.load_ingredient_list("name", query)

    def _on_ingredient_change(self, ingr: ExistingIngredient | None) -> None:
        self.amount.elem.set_unit_constraint(None if ingr is None else ingr.measurement_type.pint_unit)

    def save_and_close(self):
        if not self.check_all_input_and_show_errors():
            # TODO: Pop-up error?
            return
        new_quantity = self.amount.elem.get_quantity()
        ingredient = self.ingredient_name.elem.get_selection()
        assert ingredient is not None
        self.pantry.pantry_backend.add_vpantry_entry(ingredient, new_quantity)
        self.pantry.refresh_pantry()
        self.container.destroy()
