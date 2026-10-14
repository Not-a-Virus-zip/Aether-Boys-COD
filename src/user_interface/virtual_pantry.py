from tkinter import ttk
import tkinter as tk

import pint

from . import (
    edit_menu as em,
    user_interface_impl as ui,
)
from ..backend import (
    virtual_pantry as vp_backend,
    ingredient_list as il_backend,
    units
)
from ..backend.ingredient_list import (Ingredient, ExistingIngredient)


class VirtualPantry:
    backend: vp_backend.VirtualPantry
    ing_backend: il_backend.IngredientList
    name: str = "Virtual Pantry"
    frame: ttk.Frame
    pantry_display: ttk.Treeview
    pantry_contents: list[tuple[ExistingIngredient, pint.Quantity]]
    add_button: ttk.Button
    edit_button: ttk.Button

    def __init__(self, parent: tk.Tk | ttk.Frame, ing_backend: il_backend.IngredientList):
        self.backend = vp_backend.VirtualPantry()
        self.ing_backend = ing_backend
        self.frame = vp_frame = ttk.Frame(parent, name="virtual pantry", padding=20)
        list_frame = ttk.Frame(vp_frame)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.pantry_display = pantry_disp = ttk.Treeview(list_frame, columns=["ingr", "qty"], show="headings", selectmode=tk.BROWSE)
        scrollbar = ttk.Scrollbar(list_frame, command=pantry_disp.yview)
        pantry_disp.config(yscrollcommand=scrollbar.set)
        pantry_disp.heading("ingr", text="Ingredient")
        pantry_disp.heading("qty", text="Quantity")
        pantry_disp.column("ingr", anchor="w")
        pantry_disp.column("qty", anchor="e")

        self.pantry_contents = []
        self.refresh_pantry()
        
        scrollbar.grid(row=0, column=1, sticky="ns")
        pantry_disp.grid(row=0, column=0, sticky="news")
        list_frame.grid(row=0, column=0, columnspan=2, sticky="news")
        vp_frame.rowconfigure(0, weight=1)
        vp_frame.columnconfigure(0, weight=1)
        vp_frame.columnconfigure(1, weight=1)
        bottom_buttons: list[ttk.Button] = []
        for col, name in enumerate(("Add New", "Edit Selected")):
            button = ttk.Button(vp_frame, text=name)
            button.grid(row=1, column=col, sticky="ew")
            bottom_buttons.append(button)

        self.add_button, self.edit_button = bottom_buttons
        self.add_button.config(command=self.press_add_button)
        self.edit_button.config(command=self.press_edit_button, state=tk.DISABLED)
        pantry_disp.bind("<<TreeviewSelect>>", self.on_selection_change)

    def refresh_pantry(self):
        if len(self.pantry_contents) > 0:
            self.pantry_display.delete(*range(len(self.pantry_contents)))
        self.pantry_contents = self.backend.load_virtual_pantry_contents()
        for i, (ingr, qty) in enumerate(self.pantry_contents):
            self.pantry_display.insert("", "end", id=i, text="", values=[ingr.name, ui.fmt_qty(qty)])

    def on_selection_change(self, tv: tk.Event) -> object:
        self.edit_button.config(state=tk.NORMAL if self.is_ingr_selected() else tk.DISABLED)
    
    def is_ingr_selected(self) -> bool:
        return len(self.pantry_display.selection()) != 0

    def get_selected(self) -> tuple[ExistingIngredient, pint.Quantity] | None:
        selection = self.pantry_display.selection()
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
        self.pantry.backend.update_vpantry_entry(self.ingredient, new_quantity)
        self.pantry.refresh_pantry()
        self.container.destroy()

class VPantryAddMenu(em.EditMenu):
    pantry: VirtualPantry
    container: tk.Toplevel
    ingredient_name: em.MenuField[em.DbSearchOptions[ExistingIngredient]]
    amount: em.MenuField[em.QuantityEntry]
    save_button: ttk.Button
    cancel_button: ttk.Button

    last_search: list[ExistingIngredient]

    def __init__(self, pantry: VirtualPantry, container: tk.Toplevel) -> None:
        super().__init__(container)
        self.db_search_display = ttk.Treeview(self.frame, columns=["display"], show="headings")
        self.db_search_scrollbar = ttk.Scrollbar(self.frame, command=self.db_search_display.yview)
        self.db_search_display.config(yscrollcommand=self.db_search_scrollbar.set)
        self.db_search_display.state(("disabled",))

        self.ingredient_name = self.insert("Ingredient", em.DbSearchOptions(self.frame, self.db_search_display, "", self._search, lambda i: i.name))
        self.amount          = self.insert("Quantity", em.QuantityEntry(self.frame, 0 * units.units.dimensionless))
        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])
        self.cancel_button.configure(command=container.destroy)
        self.save_button.configure(command=self.save_and_close)
        self.pantry = pantry
        self.container = container

        self.last_search = []

        row_count = self.get_row_count()
        self.db_search_display.grid(row=1, column=3, rowspan=row_count - 3, sticky="ns")
        self.db_search_scrollbar.grid(row=1, column=4, rowspan=row_count - 3, sticky="ns")

    def _search(self, query: str) -> list[ExistingIngredient]:
        return self.pantry.ing_backend.load_ingredient_list()

    def save_and_close(self):
        new_quantity = self.amount.elem.get_quantity()
        ingredient = self.ingredient_name.elem.get_selection()
        # TODO: handle this case
        assert ingredient is not None
        self.pantry.backend.add_vpantry_entry(ingredient, new_quantity)
        self.pantry.refresh_pantry()
        self.container.destroy()
