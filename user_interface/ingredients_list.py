import tkinter as tk
from tkinter import ttk

from . import (
    edit_menu as em,
    user_interface_impl as ui
)
import dummy_business_logic_api as bl

class IngredientsList:
    name: str = "Ingredients"
    frame: ttk.Frame
    ingr_display: ttk.Treeview
    ingr_list: list[bl.Ingredient]

    add_button: ttk.Button
    edit_button: ttk.Button

    def __init__(self, parent: tk.Tk | ttk.Frame, blogic: bl.BusinessLogic):
        self.frame = ingredients_frame = ttk.Frame(parent, name="ingredients", padding=20)
        list_frame = ttk.Frame(ingredients_frame)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.ingr_display = ingr_display = ttk.Treeview(list_frame, columns=["name"], show="headings")
        scrollbar = ttk.Scrollbar(list_frame, command=ingr_display.yview)
        ingr_display.config(yscrollcommand=scrollbar.set)
        ingr_display.heading("name", text="Name")
        ingr_display.column("name", anchor="w")
        self.ingr_list = blogic.load_ingredient_list()
        for i, ingr in enumerate(self.ingr_list):
            ingr_display.insert("", "end", id=i, text="", values=[ingr])
        scrollbar.grid(row=0, column=1, sticky="ns")
        ingr_display.grid(row=0, column=0, sticky="news")
        list_frame.grid(row=0, column=0, columnspan=2, sticky="news")
        ingredients_frame.rowconfigure(0, weight=1)
        ingredients_frame.columnconfigure(0, weight=1)
        ingredients_frame.columnconfigure(1, weight=1)

        bottom_b_frame, (self.add_button, self.edit_button) = ui.make_buttons(
            ingredients_frame,
            (
                ("Add New", self.press_add_button),
                ("Edit Selected", self.press_edit_button)
            ),
            button_weight=1
        )
        bottom_b_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

    def is_ingr_selected(self) -> bool:
        return len(self.ingr_display.selection()) != 0

    def get_selected(self) -> bl.Ingredient | None:
        selection = self.ingr_display.selection()
        return None if len(selection) == 0 else self.ingr_list[int(selection[0])]
    
    def press_add_button(self):
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Create New Ingredient",
            lambda tl: IngredientEditMenu(tl, "").frame
        )

    def press_edit_button(self):
        selection = self.get_selected()
        assert selection is not None, "Edit button should be disabled when nothing is selected"
        name = selection
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Edit Ingredient",
            lambda tl: IngredientEditMenu(tl, name).frame
        )

class IngredientEditMenu(em.EditMenu):
    ingredient_name: em.MenuField[em.Entry]
    tag: em.MenuField[em.DbSearchOptions]
    fdcid: em.MenuField[em.Display]
    ingredient_measurement: em.MenuField[em.DbSearchOptions]

    def __init__(self, container: tk.Toplevel, ingredient_name: str) -> None:
        super().__init__(container)
        self.ingredient_name        = self.insert("Ingredient Name", em.Entry(self.frame, ingredient_name))
        self.tag                    = self.insert("Tag", em.DbSearchOptions(self.frame))
        # self.fdcid                  = self.insert("FDC ID", em.Display(self.frame, fdcid))
        self.ingredient_measurement = self.insert("Measurement Type", em.DbSearchOptions(self.frame))
        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])