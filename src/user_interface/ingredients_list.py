import tkinter as tk
from tkinter import ttk

from . import (
    edit_menu as em,
    user_interface_impl as ui,
)
from ..backend import (
    ingredient_list as il_backend
)
from ..backend.ingredient_list import Ingredient, ExistingIngredient

class IngredientsList:
    backend: il_backend.IngredientList

    name: str = "Ingredients"
    frame: ttk.Frame
    ingr_display: ttk.Treeview
    ingr_list: list[ExistingIngredient]

    add_button: ttk.Button
    edit_button: ttk.Button

    def __init__(self, parent: tk.Tk | ttk.Frame):
        self.backend = il_backend.IngredientList()
        self.frame = ingredients_frame = ttk.Frame(parent, name="ingredients", padding=20)
        list_frame = ttk.Frame(ingredients_frame)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.ingr_display = ingr_display = ttk.Treeview(list_frame, columns=["name", "tag", "units"], show="headings")
        scrollbar = ttk.Scrollbar(list_frame, command=ingr_display.yview)
        ingr_display.config(yscrollcommand=scrollbar.set)
        ingr_display.heading("name", text="Name")
        ingr_display.column("name", anchor="w")
        ingr_display.heading("tag", text="Tag")
        ingr_display.column("tag", anchor="e")
        ingr_display.heading("units", text="Units")
        ingr_display.column("units", anchor="e")
        self.ingr_list = self.backend.load_ingredient_list()
        for i, ingr in enumerate(self.ingr_list):
            ingr_display.insert("", "end", id=i, text="", values=[ingr.name, ingr.tag, ingr.measurement_type])# ui.fmt_qty(ingr.measurement_type)])
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

    def get_selected(self) -> ExistingIngredient | None:
        selection = self.ingr_display.selection()
        return None if len(selection) == 0 else self.ingr_list[int(selection[0])]
    
    def press_add_button(self):
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Create New Ingredient",
            lambda tl: IngredientEditMenu(self, tl, None).frame
        )

    def press_edit_button(self):
        selection = self.get_selected()
        assert selection is not None, "Edit button should be disabled when nothing is selected"
        name = selection
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Edit Ingredient",
            lambda tl: IngredientEditMenu(self, tl, name).frame
        )

class IngredientEditMenu(em.EditMenu):
    ingr_list: IngredientsList

    ingredient_name: em.MenuField[em.Entry]
    tag: em.MenuField[em.DbSearchOptions]
    # fdcid: em.MenuField[em.Display]
    ingredient_measurement: em.MenuField[em.DbSearchOptions]
    db_search_display: ttk.Treeview
    db_search_scrollbar: ttk.Scrollbar

    def __init__(self, ingr_list: IngredientsList, container: tk.Toplevel, ingredient: ExistingIngredient | None) -> None:
        self.ingr_list = ingr_list
        if ingredient is not None:
            name = ingredient.name
            tag = ingredient.tag
            measure = str(ingredient.measurement_type)
        else:
            name = ""
            tag = ""
            measure = ""

        super().__init__(container)

        self.db_search_display = ttk.Treeview(self.frame, columns=["display"], show="headings")
        self.db_search_scrollbar = ttk.Scrollbar(self.frame, command=self.db_search_display.yview)
        self.db_search_display.config(yscrollcommand=self.db_search_scrollbar.set)
        self.db_search_display.state(("disabled",))

        self.ingredient_name        = self.insert("Ingredient Name", em.Entry(self.frame, name))
        self.tag                    = self.insert("Tag", em.DbSearchOptions(self.frame, self.db_search_display, tag, self._search_tags, "Tags"))
        # self.fdcid                  = self.insert("FDC ID", em.Display(self.frame, fdcid))
        self.ingredient_measurement = self.insert("Measurement Type", em.DbSearchOptions(self.frame, self.db_search_display, measure, self._search_measurements, "Measurements"))
        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])

        row_count = self.get_row_count()
        self.db_search_display.grid(row=1, column=3, rowspan=row_count - 2, sticky="ns")
        self.db_search_scrollbar.grid(row=1, column=4, rowspan=row_count - 2, sticky="ns")

    def _search_tags(self, user_input: str) -> list[str]:
        return self.ingr_list.backend.search_ingredient_tags(user_input)

    def _search_measurements(self, user_input: str) -> list[str]:
        return [str(val) for val in self.ingr_list.backend.search_ingredient_units(user_input)]