from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Literal

from . import (
    user_interface_impl as ui,
    edit_menu as em,
)

from ..backend import (
    meal_catalog as mc_backend,
    ingredient_list as il_backend,
)

from ..backend.meal_catalog import Meal, ExistingMeal

from .scrollable_treeview import ScrollableTreeview

class MealCatalog:
    """Constructs and controls the meal catalog UI"""
    name: str = "Meal Catalog"

    backend: ui.Backend
    frame: ttk.Frame
    meal_display: ScrollableTreeview
    add_button: ttk.Button
    edit_button: ttk.Button

    def __init__(self, parent: ttk.Notebook, backend: ui.Backend) -> None:
        self.backend = backend
        self.frame = ttk.Frame(parent, name="meal catalog", padding=20)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.meal_display = ScrollableTreeview(self.frame, columns=["name", "desc"], show="headings", selectmode="browse")
        tv = self.meal_display.treeview
        tv.heading("name", text="Name")
        tv.heading("desc", text="Description")
        tv.column("name", anchor="w")
        tv.column("desc", anchor="w")

        # for meal in backend.meals.get_meals():
        #     tv.insert("", "end", text="", values=[meal.name, meal.description])
        self.meal_display.grid(row=0, column=0, columnspan=2, sticky="news")


        button_frame, (self.add_button, self.edit_button) = ui.make_buttons(self.frame, ("Add New", "Edit Selected"), button_weight=1)
        button_frame.grid(row=1, column=0, sticky="nsew")

        self.add_button.config(command=self.press_add_button)
        self.edit_button.config(command=self.press_edit_button, state=tk.DISABLED)

        self.catalog_contents = []
        self.refresh_catalog()

        tv.bind("<<TreeviewSelect>>", self._on_selection_change)
        
    def refresh_catalog(self):
        if len(self.catalog_contents) > 0:
            self.meal_display.treeview.delete(*range(len(self.catalog_contents)))
        self.catalog_contents = self.backend.meals.get_meals()
        for i, meal in enumerate(self.catalog_contents):
            self.meal_display.treeview.insert("", "end", id=i, text="", values=[meal.name,meal.description])
        
    def _on_selection_change(self, tv: tk.Event) -> object:
        self.edit_button.config(state=tk.NORMAL if self.is_meal_selected() else tk.DISABLED)
        
    def is_meal_selected(self) -> bool:
        return len(self.meal_display.treeview.selection()) != 0
        
    def get_selected(self) -> mc_backend.ExistingMeal | None:
        selection = self.meal_display.treeview.selection()
        return None if len(selection) == 0 else self.catalog_contents[int(selection[0])]

    def press_add_button(self):
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Add Meal",
            lambda tl: AlternateMealEditMenu(self, tl).frame
        )

    def press_edit_button(self):
        selection = self.get_selected()
        assert selection is not None, "Edit button should be disabled when nothing is selected"
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Edit Meal",
            lambda tl: AlternateMealEditMenu(self, tl, selection).frame
        )

class MealEditMenu(em.EditMenu):
    # I think I might want to not use the EditMenu for this one tbh
    def __init__(self, catalog: MealCatalog, container: tk.Toplevel, selected_meal: ExistingMeal | None) -> None:
        super().__init__(container)
        meal = selected_meal if selected_meal is not None else Meal("", "", None, "", "", ())

        self.image = self.insert("Image", em.Image(self.frame))
        self.name = self.insert("Name", em.Entry(self.frame, meal.name))
        self.description = self.insert("Name", em.Text(self.frame))
        self.ingredients = self.insert("Name", em.IngredientSelector(self.frame, meal.ingredients))
        self.recipe = self.insert("Name", em.Text(self.frame))

class AlternateMealEditMenu(em.EditMenu):
    def __init__(self, catalog: MealCatalog, container: tk.Toplevel, selected_meal: ExistingMeal | Meal = Meal("", "", None, "", "", ())) -> None:
        super().__init__(container)
        self.container = container
        self.catalog = catalog
        self.header_frame = ttk.Frame(self.frame)
        self.header_frame.grid(row=self.claim_row(), column=0, columnspan=3, sticky="new")
        self.image = ttk.Label(self.header_frame, image=ui.placeholder_image, padding=2, relief=tk.RIDGE)
        self.image.grid(row=0, column=0)
        mini_em = em.EditMenu(self.header_frame)
        self.name_entry = mini_em.insert("Name", em.Entry(mini_em.frame, selected_meal.name)).elem
        self.desc_entry = mini_em.insert("Description", em.Text(mini_em.frame, selected_meal.description)).elem
        mini_em.frame.grid(row=0, column=1, sticky="news")

        intermediate_row = self.claim_row()
        self.frame.rowconfigure(intermediate_row, minsize=10)

        self.ingredients_frame = ttk.Frame(self.frame)
        self.ingredients_frame.grid(row=self.claim_row(), column=0, columnspan=3, sticky="new")
        self.add_panel = IngrAddPanel(self.ingredients_frame, catalog.backend.ingredients)
        self.ingredients_frame.columnconfigure(0, weight=1, uniform="panels")
        self.add_panel.grid(row=0, column=0, sticky="new")
        self.current_panel = IngrInMeal(self.ingredients_frame)
        self.ingredients_frame.columnconfigure(2, weight=1, uniform="panels")
        self.current_panel.grid(row=0, column=2, sticky="new")

        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])
        self.cancel_button.config(command=container.destroy)
        self.save_button.config(command=self.save_and_close)

    def search_ingr(self, query: str):
        pass

    def save_and_close(self):

        self.catalog.refresh_catalog()
        self.container.destroy()

class IngrInMeal:
    def __init__(self, container: ttk.Frame) -> None:
        
        self.frame = ttk.Frame(container, padding=2)
        self.ingr_quantities = ScrollableTreeview(self.frame, columns=["name", "qty"], show="headings")
        self.frame.columnconfigure(1, weight=1, pad=4)
        self.frame.rowconfigure(1, weight=1)
        self.ingr_quantities.grid(row=1, column=0, columnspan=2, sticky="new")

        self.search_var = tk.StringVar(self.frame)
        self.quantity_editor = ttk.Entry(self.frame, textvariable=self.search_var)

        self.quantity_editor.grid(row=0, column=1, sticky="ew")
        
        self.current_ingrs = []
        
        self.qty_lbl = ttk.Label(self.frame, text="Quantity",)
        self.qty_lbl.grid(row=0, column=0)

        tv = self.ingr_quantities.treeview
        tv.heading("name", text="Name")
        tv.column("name", anchor="w", width=1)
        tv.heading("qty", text="Quantity")
        tv.column("qty", anchor="e", width=1)

        # method
        self.grid = self.frame.grid

class IngrAddPanel:
    ing_backend: il_backend.IngredientList
    frame: ttk.Frame
    ingr_display: ScrollableTreeview
    search_var: tk.StringVar
    search: ttk.Entry
    current_ingrs: list[il_backend.ExistingIngredient]
    add_button: ttk.Button

    def __init__(self, container: ttk.Frame, ing_backend: il_backend.IngredientList) -> None:
        self.ing_backend = ing_backend
        self.frame = ttk.Frame(container, padding=2)
        self.ingr_display = ScrollableTreeview(self.frame, columns=["name", "tag", "units"], show="headings")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.ingr_display.grid(row=1, column=0, columnspan=2, sticky="new")

        self.search_var = tk.StringVar(self.frame)
        self.search = ttk.Entry(self.frame, textvariable=self.search_var)
        self.search_var.trace_add("write", self._on_search_text_update)
        self.search.grid(row=0, column=0, sticky="ew")

        self.current_ingrs = []
        
        self.sort_asc = True
        self.current_sort = "ingredient"
        self.current_query = ""

        self.add_button = ttk.Button(self.frame, text="Add Ingredient")
        self.add_button.grid(row=0, column=1)
        self.frame.grid(row=0, column=1)
        tv = self.ingr_display.treeview
        tv.heading("name", text="Name", command=lambda: self.update_ingr_list(new_sort="ingredient"))
        tv.column("name", anchor="w", width=1)
        tv.heading("tag", text="Tag", command=lambda: self.update_ingr_list(new_sort="tag"))
        tv.column("tag", anchor="e", width=1)
        tv.heading("units", text="Units", command=lambda: self.update_ingr_list(new_sort="unit"))
        tv.column("units", anchor="e", width=1)

        tv.bind("<<TreeviewSelect>>", self._on_selection_update)

        self.update_ingr_list()

        # method
        self.grid = self.frame.grid

    def update_ingr_list(self, new_query: str | None = None, new_sort: Literal["ingredient", "tag", "unit"] | None = None):
        if new_query is not None:
            self.current_query = new_query
        if new_sort is not None:
            if self.current_sort == new_sort:
                self.sort_asc = not self.sort_asc
            else:
                self.current_sort = new_sort

        new_list = self.ing_backend.load_ingredient_list("ingredient", self.current_query, sort_mode=self.current_sort, asc=self.sort_asc)
        if len(self.current_ingrs) > 0:
            self.ingr_display.treeview.delete(*range(len(self.current_ingrs)))
        self.current_ingrs = new_list
        for i, ingr in enumerate(self.current_ingrs):
            self.ingr_display.treeview.insert("", "end", id=i, text="", values=[ingr.name, ingr.tag, ingr.measurement_type.name])
        

    # def fill_ingr_list(self, new_list: list[il_backend.ExistingIngredient]) -> None:
        


    def _on_selection_update(self, event: tk.Event):
        selected = self.ingr_display.treeview.selection()
        selected_count = len(selected)
        text = "Add Ingredient" if selected_count < 2 else "Add Ingredients"
        state = "disabled" if selected_count < 1 else "!disabled"
        self.add_button.state((state,))
        self.add_button.config(text=text)

    def _on_search_text_update(self, *_):
        self.update_ingr_list(new_query=self.search_var.get().strip())
