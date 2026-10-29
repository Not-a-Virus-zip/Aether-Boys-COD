from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from . import (
    edit_menu as em,
    user_interface_impl as ui,
    virtual_pantry as vp,
)
from .treeview_utilities import ScrollableTreeview, AutoSorter
from ..backend import (
    ingredient_list as il_backend,
    virtual_pantry as vp_backend,
)
from ..backend.ingredient_list import Ingredient, ExistingIngredient

class IngredientsList:
    """Constructs and controls the ingredients UI"""
    backend: il_backend.IngredientList

    virtual_pantry: vp.VirtualPantry

    name: str = "Ingredients"
    frame: ttk.Frame
    ingr_display: ScrollableTreeview
    auto_sorter: AutoSorter
    ingr_list: list[ExistingIngredient]

    add_button: ttk.Button
    edit_button: ttk.Button

    def __init__(self, parent: ttk.Notebook, virtual_pantry: vp.VirtualPantry, ing_backend: il_backend.IngredientList):
        self.backend = ing_backend

        self.virtual_pantry = virtual_pantry

        self.frame = ingredients_frame = ttk.Frame(parent, name="ingredients", padding=20)
        self.ingr_display = ScrollableTreeview(ingredients_frame, columns=["name", "tag", "unit"], show="headings")
        self.auto_sorter = AutoSorter(self.ingr_display.treeview, self._autosorter_command)
        tv = self.ingr_display.treeview
         # width=0 lets the treeview widget auto-determine the appropriate width
        tv.heading("name", text="Name")
        tv.column("name", anchor="w", width=0)
        tv.heading("tag", text="Tag")
        tv.column("tag", anchor="e", width=0)
        tv.heading("unit", text="Units")
        tv.column("unit", anchor="e", width=0)

        self.ingr_list = []
        self.refresh_ingredients(also_refresh_pantry=False)

        self.ingr_display.grid(row=0, column=0, columnspan=2, sticky="news")
        ingredients_frame.rowconfigure(0, weight=1)
        ingredients_frame.columnconfigure(0, weight=1)
        ingredients_frame.columnconfigure(1, weight=1)

        bottom_b_frame, (
            self.delete_button,
            self.add_button,
            self.edit_button,
        ) = ui.make_buttons(
            ingredients_frame,
            (
                ("Delete Ingredient", self.press_delete_button),
                ("Add New", self.press_add_button),
                ("Edit Selected", self.press_edit_button)
            ),
            button_weight=1 # buttons should expand to fill the avalable space
        )
        self.edit_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)

        bottom_b_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        tv.bind("<<TreeviewSelect>>", self.on_selection_change)

    def _autosorter_command(self, query: str, column: str, asc: bool):
        if len(self.ingr_list) > 0:
            self.ingr_display.treeview.delete(*range(len(self.ingr_list)))
        self.ingr_list = self.backend.load_ingredient_list(sort_mode=column, asc=asc)
        for i, ingr in enumerate(self.ingr_list):
            self.ingr_display.treeview.insert("", "end", id=i, text="", values=[ingr.name, ingr.tag, ingr.measurement_type.name])# ui.fmt_qty(ingr.measurement_type)])

    def refresh_ingredients(self, also_refresh_pantry=True):
        "Propagate changes from the database into the ui."
        self.auto_sorter.refresh()
        if also_refresh_pantry:
            self.virtual_pantry.refresh_pantry()

    def on_selection_change(self, tv: tk.Event) -> object:
        new_state = tk.NORMAL if self.is_ingr_selected() else tk.DISABLED
        self.edit_button.config(state=new_state)
        self.delete_button.config(state=new_state)

    def is_ingr_selected(self) -> bool:
        return len(self.ingr_display.treeview.selection()) != 0

    def get_selected(self) -> ExistingIngredient | None:
        selection = self.ingr_display.treeview.selection()
        return None if len(selection) == 0 else self.ingr_list[int(selection[0])]

    def press_delete_button(self):
        ingr = self.get_selected()
        if ingr is None:
            return

        # TODO: Warn if ingredient exists in virtual pantry
        
        if messagebox.askokcancel(
            "Confirm Deletion",
            f"Are you sure you want to delete \"{ingr.name}\" from the ingredient database?",
            icon=messagebox.WARNING,
            default=messagebox.CANCEL,
            parent=self.frame,
        ):
            try:
                self.backend.delete_ingredient(ingr.id)
            except Exception as err:
                messagebox.showerror(
                    "Deletion Failed",
                    f"Could not delete \"{ingr.name}\" from the ingredient database because it is currently used in a meal.",
                    parent=self.frame,
                )
            self.refresh_ingredients()
    
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

class IngredientEditMenu(em.EditMenuWithSearcher):
    """Constructs and controls the pop-up menu for adding/editing ingredients"""
    ingredient_name: em.MenuField[em.CheckedEntry]
    tag: em.MenuField[em.OpenDbSearchOptions]
    ingredient_measurement: em.MenuField[em.OpenDbSearchOptions]
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
            measure = ingredient.measurement_type.name
        else:
            name = ""
            tag = ""
            measure = ""

        super().__init__(container)

        name_check = em.SimpleCheck("Missing Name", bool)

        self.ingredient_name        = self.insert("Ingredient Name", em.CheckedEntry(self.frame, name_check, name))
        self.tag                    = self.insert_searcher("Tag", em.OpenDbSearchOptions(self.frame, "Tags", self._search_tags, initial_value=tag))
        self.ingredient_measurement = self.insert_searcher("Measurement Type", em.OpenDbSearchOptions(self.frame, "Measurements", self._search_measurements, initial_value=measure))
        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])

        self.cancel_button.config(command=container.destroy)
        self.save_button.config(command=self.save_and_close)

    def _search_tags(self, user_input: str) -> list[str]:
        self.tag_search_results = self.ingr_list.backend.tags_in_use(user_input)
        return self.tag_search_results

    def _search_measurements(self, user_input: str) -> list[str]:
        return self.ingr_list.backend.search_ingredient_units(user_input)

    def save_and_close(self):
        if not self.check_all_input_and_show_errors():
            # TODO: Pop-up error?
            return
        new_name = self.ingredient_name.elem.get_text()
        new_tag: str = self.tag.elem.get_text()
        new_msmnt = self.ingredient_measurement.elem.get_text()
        try:
            new_msmnt = vp_backend.into_measure_type(new_msmnt)
        except ValueError:
            print("Unknown Ingredient") # TODO: Proper error messages
            return
        if self.ingredient is None:
            self.ingr_list.backend.create_ingredient(new_name, new_tag, new_msmnt.id)
        else:
            self.ingr_list.backend.update_ingredient(self.ingredient.modify(name=new_name, tag=new_tag, measurement_type=new_msmnt))
        self.ingr_list.refresh_ingredients()
        self.container.destroy()