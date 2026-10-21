from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import (
    user_interface_impl as ui,
    edit_menu as em,
)

from ..backend import (
    meal_catalog as mc_backend,
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
        self.add_panel = IngrAddPanel(self.ingredients_frame)
        self.ingredients_frame.columnconfigure(0, weight=1)
        self.add_panel.grid(row=0, column=0, sticky="new")
        self.current_panel = IngrInMeal(self.ingredients_frame)
        self.ingredients_frame.columnconfigure(2, weight=1)
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
        self.list = ScrollableTreeview(container, columns=["name", "qty"], show="headings")
        tv = self.list.treeview
        tv.heading("name", text="Name")
        tv.column("name", anchor="w", width=1)
        tv.heading("qty", text="Quantity")
        tv.column("qty", anchor="e", width=1)
        # method
        self.grid = self.list.grid

class IngrAddPanel:
    def __init__(self, container: ttk.Frame) -> None:
        self.list = ScrollableTreeview(container, columns=["name", "tag", "units"], show="headings")

        tv = self.list.treeview
        tv.heading("name", text="Name")
        tv.column("name", anchor="w", width=1)
        tv.heading("tag", text="Tag")
        tv.column("tag", anchor="e", width=1)
        tv.heading("units", text="Units")
        tv.column("units", anchor="e", width=1)

        # method
        self.grid = self.list.grid

"""
("Image", "placeholder_img", "image"),
("Name", "Foobar Salad", "entry"),
("Description", "Insert Description Here", "text"),
("Ingredients", "Name Quantity\nFoo,10 lbs\nBar,1 gal", "list display"),
("Add Ingredients", "Lettuce,2 heads", "add ingredient"),
("", "", "separating bar"),
("Recipe (Optional)", "Insert Recipe Here", "text"),


def make_meal_catalogue(parent: tk.Tk | ttk.Frame):
    meal_frame = ttk.Frame(parent, name="meal_catalogue", padding=20)
    list_frame = ttk.Frame(meal_frame)
    list_frame.columnconfigure(0, weight=1)
    list_frame.rowconfigure(0, weight=1)
    meal_list = ttk.Treeview(list_frame, columns=["name", "desc"], show="headings")
    scrollbar = ttk.Scrollbar(list_frame, command=meal_list.yview)
    meal_list.config(yscrollcommand=scrollbar.set)
    meal_list.heading("name", text="Name")
    meal_list.heading("desc", text="Description")
    meal_list.column("name", anchor="w")
    meal_list.column("desc", anchor="w")
    example_meals = [(f"Test Meal {i}", f"Lorem Ipsum Test Description {i}") for i in range(20)]
    for name, desc in example_meals:
        meal_list.insert("", "end", text="", values=[name, desc])
    scrollbar.grid(row=0, column=1, sticky="ns")
    meal_list.grid(row=0, column=0, sticky="news")
    list_frame.grid(row=0, column=0, columnspan=2, sticky="news")
    meal_frame.rowconfigure(0, weight=1)
    meal_frame.columnconfigure(0, weight=1)
    meal_frame.columnconfigure(1, weight=1)

    edit_meal_menu = generate_edit_menu(
        [
            ("Image", "placeholder_img", "image"),
            ("Name", "Foobar Salad", "entry"),
            ("Description", "Insert Description Here", "text"),
            ("Ingredients", "Name Quantity\nFoo,10 lbs\nBar,1 gal", "list display"),
            ("Add Ingredients", "Lettuce,2 heads", "add ingredient"),
            ("", "", "separating bar"),
            ("Recipe (Optional)", "Insert Recipe Here", "text"),
        ],
        ["Cancel", 1, "Save Meal"],
    )
    for col, name in enumerate(["Add New", "Edit Selected"]):
        button = ttk.Button(meal_frame, text=name)
        button.grid(row=1, column=col, sticky="ew")
        button.config(command=lambda: em.show_edit_menu(parent.winfo_toplevel(), "Edit Meal", edit_meal_menu))
    return DummyInterface("Meal Catalog", meal_frame)
"""
