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
)
from ..backend.ingredient_list import (Ingredient, ExistingIngredient)
# import dummy_business_logic_api as bl


class VirtualPantry:
    backend: vp_backend.VirtualPantry
    name: str = "Virtual Pantry"
    frame: ttk.Frame
    pantry_display: ttk.Treeview
    pantry_contents: list[tuple[ExistingIngredient, pint.Quantity]]
    add_button: ttk.Button
    edit_button: ttk.Button

    def __init__(self, parent: tk.Tk | ttk.Frame):
        self.backend = vp_backend.VirtualPantry()
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
        print(self.get_selected())

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
        assert self.prev_quantity.is_compatible_with(new_quantity)
        self.pantry.backend.update_vpantry_entry(self.ingredient, new_quantity)
        self.pantry.refresh_pantry()
        self.container.destroy()
