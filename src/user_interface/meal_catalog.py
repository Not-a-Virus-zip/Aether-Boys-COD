from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Iterable

import pint

from . import (
    user_interface_impl as ui,
    edit_menu as em,
)

from ..backend import (
    meal_catalog as mc_backend,
    ingredient_list as il_backend,
    units,
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

        name_check = em.SimpleCheck("Missing name", bool)

        mini_em = em.EditMenu(self.header_frame)
        self.register_submenu_for_checking(mini_em)

        self.name_entry = mini_em.insert("Name", em.CheckedEntry(mini_em.frame, name_check, selected_meal.name)).elem
        self.tag_entry = mini_em.insert("Tag", em.Entry(mini_em.frame, selected_meal.tag)).elem
        self.desc_entry = mini_em.insert("Description", em.Text(mini_em.frame, selected_meal.description)).elem
        mini_em.frame.grid(row=0, column=1, sticky="news")

        self.insert_spacer_row(height=10)

        self.ingredients_frame = ttk.Frame(self.frame)
        self.ingredients_frame.grid(row=self.claim_row(), column=0, columnspan=3, sticky="new")

        self.ingredients_frame.columnconfigure(0, weight=1, uniform="panels")
        self.ingredients_frame.columnconfigure(2, weight=1, uniform="panels")

        self.current_ingredients_panel = IngrCurrentPanel(self.ingredients_frame, selected_meal.ingredients)
        self.add_ingredients_panel = IngrAddPanel(self.current_ingredients_panel, self.ingredients_frame, catalog.backend.ingredients)

        self.insert_spacer_row(height=10)
        recipe_lbl = ttk.Label(self.frame, text="Recipe")
        recipe_lbl.grid(row=self.claim_row(), column=0, columnspan=3, sticky="w")
        self.recipe_entry = em.Text(self.frame, selected_meal.recipe)
        self.recipe_entry.input_field.config(height=4)
        self.recipe_entry.direct_grid(row=self.claim_row(), column=0, columnspan=3, sticky="ew")

        self.cancel_button, self.save_button = self.finish_construction(["Cancel", 1, "Save Changes"])
        self.cancel_button.config(command=container.destroy)
        self.save_button.config(command=self.save_and_close)

    def collect_changes_into_meal(self) -> ExistingDetailedMeal | DetailedMeal:
        return self.meal.modify(
            name=self.name_entry.get_text(),
            tag=self.tag_entry.get_text(),
            description=self.desc_entry.get_text(),
            # picture=,
            recipe=self.recipe_entry.get_text(),
            ingredients=tuple(self.current_ingredients_panel.get_ingredients())
        )

    def save_and_close(self):
        if not self.check_all_input_and_show_errors():
            # TODO: Pop-up error?
            return
        
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

        self.quantity_label = ttk.Label(frame, text="Curr. Ingredients")
        self.quantity_label.grid(row=0, column=2, sticky="ew")

        self.quantity_var = tk.StringVar(frame)
        self.quantity_editor = ttk.Entry(frame, textvariable=self.quantity_var)
        self.quantity_editor.bind("<KeyPress-Return>", self._on_quantity_editor_return)
        self.quantity_var.trace_add("write", self._on_quantity_text_update)

        self.quantity_editor.grid(row=2, column=2, sticky="ew")

        self.confirm_button = ttk.Button(frame)
        self.confirm_button.grid(row=3, column=2, sticky="ew")

        self.error_display = ttk.Label(frame)

        prev_width = 0
        def on_config(event: tk.Event):
            nonlocal prev_width
            if event.width != prev_width:
                self.error_display.config(wraplength=event.width)
                prev_width = event.width

        self.error_display.bind("<Configure>", on_config)
        self.error_display.grid(row=4, column=2, sticky="new")
        frame.rowconfigure(4, minsize=2 + self.error_display.winfo_reqheight() * 3)

        self._disable_qty_editor()

        self.display_len = 0
        self.current_ingrs = list(starting_ingredients)
        self.editing_index: int | None = None
        self.current_ingredient_ids = {ing.id for ing, _ in self.current_ingrs}
        

        tv = self.ingr_quantities
        tv.heading("name", text="Name")
        tv.column("name", anchor="w", width=1)
        tv.heading("qty", text="Quantity")
        tv.column("qty", anchor="e", width=1)

        self.do_selection_update = True
        tv.bind("<<TreeviewSelect>>", self._on_selection_update)

        self.auto_sorter = AutoSorter(self.ingr_quantities, self._autosorter_command)
        self.update_quantity_list()

    def _disable_qty_editor(self):
        self.quantity_editor.state(("disabled",))
        self.confirm_button.state(("disabled",))
        self.confirm_button.config(text="Select an Ingredient")
        self.error_display.config(text="")

    def _enable_qty_editor(self):
        self.quantity_editor.state(("!disabled",))

    def _on_quantity_editor_return(self, event: tk.Event):
        if self.quantity_editor.instate(("!disabled",)) and self.confirm_button.instate(("!disabled",)):
            self.confirm_button.invoke()

    def _on_selection_update(self, event: tk.Event):
        selection = self.ingr_quantities.selection()
        if len(selection) == 0:
            self._disable_qty_editor()
            return
        self._enable_qty_editor()

        ingr_index = int(selection[0])
        # Do nothing if the selected item is the same as the one being edited currently
        if ingr_index == self.editing_index:
            return
        ingr, qty = self.current_ingrs[ingr_index]
        self.editing_index = ingr_index
        self.quantity_editor.delete(0, tk.END)
        self.quantity_editor.insert(tk.END, str(qty))

    def _on_quantity_text_update(self, *args):
        self.update_confirm_button()

    def update_confirm_button(self):
        if self.editing_index is None:
            return
        active_ingr, curr_qty = self.current_ingrs[self.editing_index]
        current_text = self.quantity_var.get()

        def set_mode_no_change():
            self.confirm_button.state(("disabled",))
            self.confirm_button.config(
                text=f"...",
                command=""
            )
            self.error_display.config(text="")

        def set_mode_delete():
            self.confirm_button.state(("!disabled",))
            self.confirm_button.config(
                text=f"Remove {active_ingr.name}",
                command=lambda: self._do_remove_active_ingr(active_ingr.id)
            )
            self.error_display.config(text="")

        def set_mode_error(text: str):
            self.confirm_button.state(("disabled",))
            self.confirm_button.config(text="Error", command="")
            self.error_display.config(text=text)

        def set_mode_success(new_quantity: pint.Quantity):
            self.confirm_button.state(("!disabled",))
            self.confirm_button.config(
                text=f"Set {active_ingr.name} to {ui.fmt_qty(new_quantity)}",
                command=lambda: self._update_active_ingr_qty(active_ingr.id, new_quantity)
            )
            self.error_display.config(text="")
        
        if not current_text:
            set_mode_delete()
            return
        try:
            new_qty = units.interpret_quantity(current_text)
        except Exception as e:
            set_mode_error(str(e))
            return
        if new_qty.unitless:
            new_qty *= curr_qty.units
        expected_unit = active_ingr.measurement_type.pint_unit
        if not new_qty.is_compatible_with(expected_unit):
            set_mode_error(f"Incompatible units {new_qty.units} and {expected_unit}")
            return
        
        # if user hasn't changed the quantity or the units for that quantity, the button should be disabled
        if new_qty == curr_qty and new_qty.units == curr_qty.units:
            set_mode_no_change()
            return
        set_mode_success(new_qty)

    def _update_active_ingr_qty(self, expected_id: int, new_quantity: pint.Quantity):
        assert self.editing_index is not None
        ingr, prev_qty = self.current_ingrs[self.editing_index]
        assert ingr.id == expected_id
        assert ingr.measurement_type.pint_unit.is_compatible_with(new_quantity)
        self.current_ingrs[self.editing_index] = ingr, new_quantity
        self.update_quantity_list()

    def _do_remove_active_ingr(self, expected_id: int):
        assert self.editing_index is not None
        assert self.current_ingrs[self.editing_index][0].id == expected_id
        del self.current_ingrs[self.editing_index]
        self.update_quantity_list()

    def get_ingredients(self) -> list[tuple[ExistingIngredient, pint.Quantity]]:
        return self.current_ingrs

    def update_quantity_list(self):
        self.auto_sorter.refresh()
        self.update_confirm_button()

    def _autosorter_command(self, query: str, column: str, asc: bool):
        if self.display_len > 0:
            self.ingr_quantities.delete(*range(self.display_len))

        # was there an item already selected?
        selected_ingr = (
            self.current_ingrs[self.editing_index]
            if self.editing_index is not None else None
        )

        key = {
            "name": lambda t: t[0].name,
            "qty": lambda t: t[1].magnitude
        }[column]
        self.current_ingrs.sort(key=key, reverse=not asc)
        for i, (ingr, qty) in enumerate(self.current_ingrs):
            self.ingr_quantities.insert("", "end", id=i, text="", values=[ingr.name, ui.fmt_qty(qty)])
        if selected_ingr is not None:
            self.editing_index = self.current_ingrs.index(selected_ingr)
            self.ingr_quantities.selection_set(self.editing_index)
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
        self.search_frame.columnconfigure(0, weight=4)
        self.search_frame.columnconfigure(1, weight=3)
        self.search_frame.columnconfigure(2, weight=5)
        self.search_frame.grid(row=0, column=0, sticky="ew")

        self.add_label = ttk.Label(self.search_frame, text="Add Ingredients")
        self.add_label.grid(row=0, column=0, sticky="ew")

        self.search_var = tk.StringVar(frame)
        self.search = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_var.trace_add("write", self._on_search_text_update)
        self.search.grid(row=0, column=2, sticky="ew")

        self.current_ingrs = []


        self.add_button = ttk.Button(frame, text="Add Ingredient", command=self.on_press_add_button, state=tk.DISABLED)
        self.add_button.grid(row=2, column=0, sticky="ew")

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
