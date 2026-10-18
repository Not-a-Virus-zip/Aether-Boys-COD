from __future__ import annotations

from tkinter import Toplevel, ttk

from . import (
    user_interface_impl as ui,
    edit_menu as em,
)
from .scrollable_treeview import TreeviewScroll

class MealCatalog:
    """Constructs and controls the meal catalog UI"""
    name: str = "Meal Catalog"

    frame: ttk.Frame
    add_button: ttk.Button
    edit_button: ttk.Button

    def __init__(self, parent: ttk.Notebook, backend: ui.Backend) -> None:
        self.frame = ttk.Frame(parent, name="meal_catalog")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        meal_list = TreeviewScroll(self.frame, columns=["name", "desc"], show="headings")
        meal_list.treeview.heading("name", text="Name")
        meal_list.treeview.heading("desc", text="Description")
        meal_list.treeview.column("name", anchor="w")
        meal_list.treeview.column("desc", anchor="w")

        
        for meal in backend.meals.get_meals():
            meal_list.treeview.insert("", "end", text="", values=[meal.name, meal.description])
        meal_list.grid(row=0, column=0, columnspan=2, sticky="news")
        

        button_frame, (self.add_button, self.edit_button) = ui.make_buttons(self.frame, ("Add New", "Edit Selected"), button_weight=1)
        button_frame.grid(row=1, column=0, sticky="nsew")

        self.add_button.config(command=self.press_add_button)
        self.edit_button.config(command=self.press_edit_button)

    def press_add_button(self):
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Add Ingredient",
            lambda tl: MealEditMenu(self, tl).frame
        )

    def press_edit_button(self):
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Add Ingredient",
            lambda tl: MealEditMenu(self, tl).frame
        )

class MealEditMenu(em.EditMenu):
    def __init__(self, catalog: MealCatalog, parent: Toplevel) -> None:
        super().__init__(parent)
        self.image = self.insert("Image", em.Image(self.frame))
        self.name = self.insert("Name", em.Entry(self.frame))
        self.description = self.insert("Name", em.Text(self.frame))
        self.Ingredients = self.insert("Name", em.IngredientSelector(self.frame))
        self.recipe = self.insert("Name", em.Text(self.frame))


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
