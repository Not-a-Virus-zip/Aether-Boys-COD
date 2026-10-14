import tkinter as tk
from tkinter import ttk

from . import (
    edit_menu as em,
    user_interface_impl as ui,
    virtual_pantry as vp,
)
from ..backend import (
    ingredient_list as il_backend
)
from ..backend.ingredient_list import Ingredient, ExistingIngredient

class IngredientsList:
    backend: il_backend.IngredientList

    virtual_pantry: vp.VirtualPantry

    name: str = "Ingredients"
    frame: ttk.Frame
    ingr_display: ttk.Treeview
    ingr_list: list[ExistingIngredient]

    add_button: ttk.Button
    edit_button: ttk.Button

    def __init__(self, parent: tk.Tk | ttk.Frame, virtual_pantry: vp.VirtualPantry, ing_backend: il_backend.IngredientList):
        self.backend = ing_backend

        self.virtual_pantry = virtual_pantry

        self.frame = ingredients_frame = ttk.Frame(parent, name="ingredients", padding=20)
        list_frame = ttk.Frame(ingredients_frame)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.ingr_display = ingr_display = ttk.Treeview(list_frame, columns=["name", "tag", "units"], show="headings")
        scrollbar = ttk.Scrollbar(list_frame, command=ingr_display.yview)
        ingr_display.config(yscrollcommand=scrollbar.set)

        # Note: for some reason, setting width=1 causes all columns distribute evenly. I don't know why.
        ingr_display.heading("name", text="Name")
        ingr_display.column("name", anchor="w", width=1)
        ingr_display.heading("tag", text="Tag")
        ingr_display.column("tag", anchor="e", width=1)
        ingr_display.heading("units", text="Units")
        ingr_display.column("units", anchor="e", width=1)

        self.ingr_list = []
        self.refresh_ingredients()

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
        self.edit_button.config(state=tk.DISABLED)
        bottom_b_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        ingr_display.bind("<<TreeviewSelect>>", self.on_selection_change)

    def refresh_ingredients(self):
        if len(self.ingr_list) > 0:
            self.ingr_display.delete(*range(len(self.ingr_list)))
        self.ingr_list = self.backend.load_ingredient_list()
        for i, ingr in enumerate(self.ingr_list):
            self.ingr_display.insert("", "end", id=i, text="", values=[ingr.name, ingr.tag, ingr.measurement_type])# ui.fmt_qty(ingr.measurement_type)])
        self.virtual_pantry.refresh_pantry()

    def on_selection_change(self, tv: tk.Event) -> object:
        self.edit_button.config(state=tk.NORMAL if self.is_ingr_selected() else tk.DISABLED)

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
        selected_ingredient = selection
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Edit Ingredient",
            lambda tl: IngredientEditMenu(self, tl, selected_ingredient).frame
        )

class IngredientEditMenu(em.EditMenu):
    ingredient_name: em.MenuField[em.Entry]
    tag: em.MenuField[em.DbSearchOptions[str]]
    # fdcid: em.MenuField[em.Display]
    ingredient_measurement: em.MenuField[em.DbSearchOptions]
    db_search_display: ttk.Treeview
    db_search_scrollbar: ttk.Scrollbar
    container: tk.Toplevel

    ingr_list: IngredientsList
    ingredient: ExistingIngredient | None

    def __init__(self, ingr_list: IngredientsList, container: tk.Toplevel, ingredient: ExistingIngredient | None) -> None:
        self.ingr_list = ingr_list
        self.container = container
        self.tag_search_results = []
        self.ingredient = ingredient
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
        self.tag                    = self.insert("Tag", em.DbSearchOptions(self.frame, self.db_search_display, tag, self._search_tags, lambda t: t, "Tags"))
        # self.fdcid                  = self.insert("FDC ID", em.Display(self.frame, fdcid))
        self.ingredient_measurement = self.insert("Measurement Type", em.DbSearchOptions(self.frame, self.db_search_display, measure, self._search_measurements, lambda t: t, "Measurements"))
        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])

        self.cancel_button.config(command=container.destroy)
        self.save_button.config(command=self.save_and_close)
        row_count = self.get_row_count()
        self.db_search_display.grid(row=1, column=3, rowspan=row_count - 3, sticky="ns")
        self.db_search_scrollbar.grid(row=1, column=4, rowspan=row_count - 3, sticky="ns")

    def _search_tags(self, user_input: str) -> list[str]:
        self.tag_search_results = self.ingr_list.backend.tags_in_use(user_input)
        return [tag.name for tag in self.tag_search_results]

    def _search_measurements(self, user_input: str) -> list[str]:
        return self.ingr_list.backend.search_ingredient_units(user_input)

    def save_and_close(self):
        new_name = self.ingredient_name.elem.get_text()
        new_tag: str = self.tag.elem.get_text()
        new_msmnt = self.ingredient_measurement.elem.get_text()

        if self.ingredient is None:
            self.ingr_list.backend.create_ingredient(new_name, new_tag, new_msmnt)
        else:
            self.ingr_list.backend.update_ingredient(self.ingredient.id, new_name,  new_tag, new_msmnt)
        self.ingr_list.refresh_ingredients()
        self.container.destroy()