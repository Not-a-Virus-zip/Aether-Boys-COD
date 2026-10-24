from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Iterable, Callable

import pint

from . import (
    user_interface_impl as ui,
    edit_menu as em,
)

from ..backend import (
    meal_catalog as mc_backend,
    ingredient_list as il_backend,
)

from ..backend.meal_catalog import ExistingSimpleMeal, ExistingDetailedMeal, DetailedMeal
from ..backend.ingredient_list import ExistingIngredient

from .treeview_utilities import ScrollableTreeview, link_treeview_to_scrollbar, AutoSorter

class MealCatalog:
    """Constructs and controls the meal catalog UI"""
    name: str = "Meal Catalog"

    backend: ui.Backend
    frame: ttk.Frame
    meal_display: ScrollableTreeview
    add_button: ttk.Button
    edit_button: ttk.Button
    catalog_contents: list[ExistingSimpleMeal]


    def __init__(self, parent: ttk.Notebook, backend: ui.Backend) -> None:
        self.backend = backend
        self.frame = ttk.Frame(parent, name="meal catalog", padding=20)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.meal_display = ScrollableTreeview(self.frame, columns=["name", "tag", "desc"], show="headings", selectmode="browse")
        self.auto_sorter = AutoSorter(self.meal_display.treeview, self._autosorter_command, use_columns=["name", "tag"])
        tv = self.meal_display.treeview
        tv.heading("name", text="Name")
        tv.column("name", anchor="w", width=50)
        tv.heading("tag", text="Tag")
        tv.column("tag", anchor="w", width=0)
        tv.heading("desc", text="Description")
        tv.column("desc", anchor="w", width=100)

        self.meal_display.grid(row=0, column=0, columnspan=2, sticky="news")


        button_frame, (self.add_button, self.edit_button) = ui.make_buttons(self.frame, ("Add New", "Edit Selected"), button_weight=1)
        button_frame.grid(row=1, column=0, sticky="nsew")

        self.add_button.config(command=self.press_add_button)
        self.edit_button.config(command=self.press_edit_button, state=tk.DISABLED)

        self.catalog_contents = []
        self.refresh_catalog()

        tv.bind("<<TreeviewSelect>>", self._on_selection_change)

    def _autosorter_command(self, query: str, column: str, asc: bool):
        if len(self.catalog_contents) > 0:
            self.meal_display.treeview.delete(*range(len(self.catalog_contents)))
        self.catalog_contents = self.backend.meals.get_simple_meals(column, asc)
        for i, meal in enumerate(self.catalog_contents):
            self.meal_display.treeview.insert("", "end", id=i, text="", values=[meal.name, meal.tag, meal.description])
    
    def refresh_catalog(self):
        self.auto_sorter.refresh()
        
    def _on_selection_change(self, tv: tk.Event) -> object:
        self.edit_button.config(state=tk.NORMAL if self.is_meal_selected() else tk.DISABLED)
        
    def is_meal_selected(self) -> bool:
        return len(self.meal_display.treeview.selection()) != 0
        
    def get_selected(self) -> mc_backend.ExistingSimpleMeal | None:
        selection = self.meal_display.treeview.selection()
        return None if len(selection) == 0 else self.catalog_contents[int(selection[0])]

    def press_add_button(self):
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Add Meal",
            lambda tl: MealEditMenu(self, tl).frame
        )

    def press_edit_button(self):
        selection = self.get_selected()
        assert selection is not None, "Edit button should be disabled when nothing is selected"
        full_meal = self.backend.meals.get_detailed_meal(selection.id)
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Edit Meal",
            lambda tl: MealEditMenu(self, tl, full_meal).frame
        )

empty_detailed_meal = DetailedMeal(
    name="",
    tag="",
    description="",
    picture="",
    recipe="",
    ingredients=()
)

class MealEditMenu(em.EditMenu):
    def __init__(self, catalog: MealCatalog, container: tk.Toplevel, selected_meal: ExistingDetailedMeal | DetailedMeal = empty_detailed_meal) -> None:
        super().__init__(container)
        self.container = container
        self.catalog = catalog
        self.meal = selected_meal
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

        self.ingredients_frame.columnconfigure(0, weight=1, uniform="panels")
        self.ingredients_frame.columnconfigure(2, weight=1, uniform="panels")

        self.current_ingredients_panel = IngrCurrentPanel(self.ingredients_frame, selected_meal.ingredients)
        self.add_ingredients_panel = IngrAddPanel(self.current_ingredients_panel, self.ingredients_frame, catalog.backend.ingredients)
        # self.add_panel.grid(row=0, column=0, sticky="new")
        

        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])
        self.cancel_button.config(command=container.destroy)
        self.save_button.config(command=self.save_and_close)

    def collect_changes_into_meal(self) -> ExistingDetailedMeal | DetailedMeal:
        return self.meal.modify(
            name=self.name_entry.get_text(),
            # tag=,
            description=self.desc_entry.get_text(),
            # picture=,
            # recipe=,
            ingredients=tuple(self.current_ingredients_panel.get_ingredients())
        )

    def save_and_close(self):
        match self.collect_changes_into_meal():
            case ExistingDetailedMeal() as meal:
                self.catalog.backend.meals.update_meal(meal)
            case DetailedMeal() as meal:
                self.catalog.backend.meals.create_meal(meal)
        self.catalog.refresh_catalog()
        self.container.destroy()

class IngrCurrentPanel:
    def __init__(self, frame: ttk.Frame, starting_ingredients: Iterable[tuple[ExistingIngredient, pint.Quantity]]) -> None:
        self.ingr_quantities = ttk.Treeview(frame, columns=["name", "qty"], show="headings", selectmode="browse")
        scrollbar = ttk.Scrollbar(frame)
        link_treeview_to_scrollbar(self.ingr_quantities, scrollbar)
        self.ingr_quantities.grid(row=1, column=2, sticky="new")
        scrollbar.grid(row=1, column=3, sticky="ns")

        self.quantity_frame = ttk.Frame(frame)
        self.quantity_frame.columnconfigure(1, weight=1)
        self.quantity_frame.grid(row=0, column=2, sticky="ew")
        self.quantity_var = tk.StringVar(self.quantity_frame)
        self.quantity_editor = ttk.Entry(self.quantity_frame, textvariable=self.quantity_var)

        self.quantity_editor.grid(row=0, column=1, sticky="ew")

        self.display_len = 0
        self.current_ingrs = list(starting_ingredients)
        self.current_ingredient_ids = {ing.id for ing, _ in self.current_ingrs}
        
        self.qty_lbl = ttk.Label(self.quantity_frame, text="Quantity",)
        self.qty_lbl.grid(row=0, column=0)

        tv = self.ingr_quantities
        tv.heading("name", text="Name")
        tv.column("name", anchor="w", width=1)
        tv.heading("qty", text="Quantity")
        tv.column("qty", anchor="e", width=1)

        tv.bind("<<TreeviewSelect>>", self._on_selection_update)

        self.auto_sorter = AutoSorter(self.ingr_quantities, self._autosorter_command)
        self.update_quantity_list()

    def _on_selection_update(self, event: tk.Event):
        selection = self.ingr_quantities.selection()
        if len(selection) == 0:
            return
        selected_entry = self.current_ingrs[int(selection[0])]


    def get_ingredients(self) -> list[tuple[ExistingIngredient, pint.Quantity]]:
        return self.current_ingrs

    def update_quantity_list(self):
        self.auto_sorter.refresh()

    def _autosorter_command(self, query: str, column: str, asc: bool):
        if self.display_len > 0:
            self.ingr_quantities.delete(*range(self.display_len))

        key = {
            "name": lambda t: t[0].name,
            "qty": lambda t: t[1].magnitude
        }[column]
        self.current_ingrs.sort(key=key, reverse=not asc)
        for i, (ingr, qty) in enumerate(self.current_ingrs):
            self.ingr_quantities.insert("", "end", id=i, text="", values=[ingr.name, ui.fmt_qty(qty)])
        self.display_len = len(self.current_ingrs)
    
    def add_ingredients(self, ingrs: tuple[ExistingIngredient, ...]):
        assert self.current_ingredient_ids.isdisjoint(i.id for i in ingrs)
        self.current_ingredient_ids.update(i.id for i in ingrs)
        self.current_ingrs.extend((ing, 1 * ing.measurement_type.pint_unit) for ing in ingrs)
        self.update_quantity_list()

    def is_ingr_not_in_meal(self, ing: ExistingIngredient) -> bool:
        return ing.id not in self.current_ingredient_ids


class IngrAddPanel:
    other_panel: IngrCurrentPanel
    ing_backend: il_backend.IngredientList
    ingr_display: ttk.Treeview
    search_var: tk.StringVar
    search: ttk.Entry
    current_ingrs: list[ExistingIngredient]
    add_button: ttk.Button
    

    def __init__(self, other_panel: IngrCurrentPanel, frame: ttk.Frame, ing_backend: il_backend.IngredientList) -> None:
        self.other_panel = other_panel
        self.ing_backend = ing_backend
        self.ingr_display = ttk.Treeview(frame, columns=["name", "tag", "unit"], show="headings")
        scrollbar = ttk.Scrollbar(frame)
        link_treeview_to_scrollbar(self.ingr_display, scrollbar)
        self.ingr_display.grid(row=1, column=0, sticky="new")
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.search_frame = ttk.Frame(frame)
        self.search_frame.columnconfigure(0, weight=1)
        self.search_frame.grid(row=0, column=0, sticky="ew")

        self.search_var = tk.StringVar(frame)
        self.search = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_var.trace_add("write", self._on_search_text_update)
        self.search.grid(row=0, column=0, sticky="ew")

        self.current_ingrs = []


        self.add_button = ttk.Button(self.search_frame, text="Add Ingredient", command=self.on_press_add_button, state=tk.DISABLED)
        self.add_button.grid(row=0, column=1)

        tv = self.ingr_display
        tv.heading("name", text="Name")
        tv.column("name", anchor="w", width=1)
        tv.heading("tag", text="Tag")
        tv.column("tag", anchor="e", width=1)
        tv.heading("unit", text="Units")
        tv.column("unit", anchor="e", width=1)

        self.auto_sorter = AutoSorter(self.ingr_display, self._autosorter_command)

        tv.bind("<<TreeviewSelect>>", self._on_selection_update)

        self.update_ingr_list()

    def on_press_add_button(self):
        self.other_panel.add_ingredients(tuple(
            self.current_ingrs[int(index)]
            for index in self.ingr_display.selection()
        ))
        self.update_ingr_list()

    def _autosorter_command(self, query: str, column: str, asc: bool):
        new_list = self.ing_backend.load_ingredient_list("name", query, sort_mode=column, asc=asc)
        new_list = list(filter(self.other_panel.is_ingr_not_in_meal, new_list))
        if len(self.current_ingrs) > 0:
            self.ingr_display.delete(*range(len(self.current_ingrs)))
        self.current_ingrs = new_list
        for i, ingr in enumerate(self.current_ingrs):
            self.ingr_display.insert("", "end", id=i, text="", values=[ingr.name, ingr.tag, ingr.measurement_type.name])

    def update_ingr_list(self):
        self.auto_sorter.refresh()

    def _on_selection_update(self, event: tk.Event):
        selected = self.ingr_display.selection()
        selected_count = len(selected)
        text = "Add Ingredient" if selected_count < 2 else "Add Ingredients"
        state = "disabled" if selected_count < 1 else "!disabled"
        self.add_button.state((state,))
        self.add_button.config(text=text)

    def _on_search_text_update(self, *_):
        self.auto_sorter.update_query(self.search_var.get().strip())
