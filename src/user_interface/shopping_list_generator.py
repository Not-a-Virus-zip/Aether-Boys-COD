from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import datetime as dt

import pint

from ..backend.ingredient_list import ExistingIngredient
from ..backend.shopping_list_generator import (
    ShoppingList,
    CurrentShoppingTrip,
    ShoppingTripResults,
)
from ..backend import (
    units,
    shopping_list_generator as sl_backend,
)
from .treeview_tools import AutoSorter, ScrollableTreeview, add_double_click_command
from . import (
    user_interface_impl as ui,
    virtual_pantry as vp,
)

type UIMode = CreateNewListUI | ShowCurrentListUI

class ShoppingListGeneratorUI:
    name: str = "Your Shopping List"

    def __init__(self, parent: ttk.Notebook, pantry: vp.VirtualPantry, backend: ui.Backend) -> None:
        self.frame = ttk.Frame(parent, name="shopping", padding=20)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.backend = backend

        self.pantry = pantry

        self.generator = CreateNewListUI(self.frame, self)
        self.trip_display = ShowCurrentListUI(self.frame, self)

        self.current: UIMode | None = None
        backend.generator.get_current_shopping_trip()
        self._swap_in_ui(self.generator)

    def _swap_in_ui(self, mode: UIMode):
        if self.current is not None:
            self.current.frame.grid_forget()
        mode.frame.grid(row=0, column=0, sticky="nsew")
        self.current = mode

    def cancel_shopping_trip(self, trip: CurrentShoppingTrip):
        self.backend.generator.cancel_shopping_trip(trip)
        self._swap_in_ui(self.generator)

    def start_shopping_trip(self, shopping_list: ShoppingList):
        trip = self.backend.generator.start_shopping_trip(shopping_list)
        self.trip_display.set_current_trip(trip)
        self._swap_in_ui(self.trip_display)

    def finish_shopping_trip(self, trip: ShoppingTripResults):
        self.backend.generator.complete_shopping_trip(trip)
        self.pantry.refresh_pantry()
        self._swap_in_ui(self.generator)

class CreateNewListUI:
    def __init__(self, frame: ttk.Frame, main_ui: ShoppingListGeneratorUI):
        self.frame = ttk.Frame(frame)
        self.main_ui = main_ui

        duration_frame = ttk.Frame(self.frame, padding=4)
        duration_label = ttk.Label(duration_frame, text="Covering meals for the next")
        self.duration_error_label = ttk.Label(duration_frame)
        duration_entry = ttk.Combobox(duration_frame, values=DURATION_OPTIONS)
        self.duration_var = tk.StringVar(duration_entry)
        duration_entry.config(textvariable=self.duration_var)
        self.duration_var.trace_add("write", self._on_duration_modified)

        duration_label.grid(row=0, column=0)
        duration_entry.grid(row=0, column=1)
        self.duration_error_label.grid(row=1, column=0, columnspan=2, sticky="e")
        duration_frame.grid(row=0, column=0, columnspan=2)

        self.shopping_list_disp = ScrollableTreeview(self.frame, columns=["ingr", "qty"], show="headings")
        tv = self.shopping_list_disp.treeview
        tv.heading("ingr", text="Ingredient")
        tv.heading("qty", text="Quantity")
        tv.column("ingr", anchor="w")
        tv.column("qty", anchor="e")

        self.shopping_list = None
        self.ingr_list: list[tuple[ExistingIngredient, pint.Quantity]] = []
        self.display_len = 0
        self.editing_index = None

        self.auto_sorter = AutoSorter(self.shopping_list_disp.treeview, self._autosorter_command, use_columns=["ingr", "qty"])

        self.shopping_list_disp.grid(row=1, column=0, columnspan=2, sticky="news")
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        b_frame, (self.go_shopping_button,) = ui.make_buttons(
            self.frame,
            (("Go Shopping", self.press_go_shopping),),
            button_weight=1,
        )
        b_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        # default duration is 1 week
        duration_entry.current(7)

    def press_go_shopping(self):
        if self.shopping_list is not None:
            self.main_ui.start_shopping_trip(self.shopping_list)

    def _on_duration_modified(self, *_):
        user_input = self.duration_var.get()
        match parse_duration_input(dt.date.today(), user_input):
            case Exception() as e:
                self.duration_error_label.config(text=str(e))
            case span:
                self.duration_error_label.config(text="")
                self.update_shopping_preview(span)
    
    def update_shopping_preview(self, span: tuple[dt.date, dt.date]):
        self.shopping_list = self.main_ui.backend.generator.get_needed_ingredients(*span)
        self.ingr_list = list(self.shopping_list.ingredients_needed)
        self.editing_index = None
        self.auto_sorter.refresh()
    
    def _autosorter_command(self, query: str, column: str, asc: bool):
        tv = self.shopping_list_disp.treeview
        if self.display_len > 0:
            tv.delete(*range(self.display_len))

        # was there an item already selected?
        selected_ingr = (
            self.ingr_list[self.editing_index]
            if self.editing_index is not None else None
        )

        key = {
            "ingr": lambda t: t[0].name,
            "qty": lambda t: t[1].magnitude
        }[column]
        self.ingr_list.sort(key=key, reverse=not asc)
        for i, (ingr, qty) in enumerate(self.ingr_list):
            tv.insert("", "end", id=i, text="", values=[ingr.name, ui.fmt_qty(qty)], tags=["cl"])
        if selected_ingr is not None:
            self.editing_index = self.ingr_list.index(selected_ingr)
            tv.selection_set(self.editing_index)
        self.display_len = len(self.ingr_list)

class ShowCurrentListUI:
    def __init__(self, frame: ttk.Frame, main_ui: ShoppingListGeneratorUI):
        self.frame = ttk.Frame(frame)
        self.main_ui = main_ui

        duration_frame = ttk.Frame(self.frame, padding=4)
        self.duration_label = ttk.Label(duration_frame, text="Trip covering meals for the next")

        self.duration_label.grid(row=0, column=0)
        duration_frame.grid(row=0, column=0)

        self.shopping_list_disp = ScrollableTreeview(self.frame, columns=["ingr", "qty"], show="headings")
        tv = self.shopping_list_disp.treeview
        tv.heading("ingr", text="Ingredient")
        tv.heading("qty", text="Quantity")
        tv.column("ingr", anchor="w")
        tv.column("qty", anchor="e")

        self.auto_sorter = AutoSorter(self.shopping_list_disp.treeview, self._autosorter_command, use_columns=["ingr", "qty"])

        add_double_click_command(tv, "cl", self._on_double_click)

        self.current_trip = None
        self.ingr_list: list[tuple[ExistingIngredient, pint.Quantity]] = []
        self.display_len = 0

        self.modifications: dict[ExistingIngredient, pint.Quantity] = {}
        # self.ingr_indices: dict[ExistingIngredient, int]

        self.shopping_list_disp.grid(row=1, column=0, sticky="news")
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.quantity_var = tk.StringVar(self.frame)
        self.quantity_editor = ttk.Entry(self.frame, textvariable=self.quantity_var)
        self.quantity_editor.bind("<KeyPress-Return>", self._on_quantity_editor_return)
        self.quantity_var.trace_add("write", self._on_quantity_text_update)
        
        self.quantity_editor.grid(row=2, column=0, sticky="ew")
        
        self.confirm_button = ttk.Button(self.frame)
        self.confirm_button.grid(row=3, column=0, sticky="ew")
        
        self.error_display = ttk.Label(self.frame)
        
        prev_width = 0
        def on_config(event: tk.Event):
            nonlocal prev_width
            if event.width != prev_width:
                self.error_display.config(wraplength=event.width)
                prev_width = event.width
        
        self.error_display.bind("<Configure>", on_config)
        self.error_display.grid(row=4, column=0, sticky="new")
        frame.rowconfigure(4, minsize=2 + self.error_display.winfo_reqheight() * 3)
        
        self.display_len = 0
        self.editing_index: int | None = None
        # self.current_ingredient_ids = {ing.id for ing, _ in self.ingr_list}
        
        self._disable_qty_editor()
        
        self.do_selection_update = True
        tv.bind("<<TreeviewSelect>>", self._on_selection_update)
        
        
        self.update_confirm_button()

        b_frame, (self.cancel_trip_button, self.finish_trip_button) = ui.make_buttons(
            self.frame,
            (
                ("Cancel Trip", self.on_press_cancel),
                ("Finish Trip", self.on_press_finish),
            ),
            button_weight=1,
        )
        b_frame.grid(row=5, column=0, columnspan=2, sticky="ew")
    
    def on_press_cancel(self):
        if self.current_trip is None:
            self.main_ui._swap_in_ui(self.main_ui.generator)
        else:
            self.main_ui.cancel_shopping_trip(self.current_trip)

    def on_press_finish(self):
        assert self.current_trip is not None
        results = ShoppingTripResults(
            self.current_trip,
            tuple(
                (ingr, self.modifications.get(ingr) or qty)
                for ingr, qty in self.current_trip.ingredients_needed
            )
        )
        self.main_ui.finish_shopping_trip(results)

    def set_current_trip(self, trip: sl_backend.CurrentShoppingTrip):
        self.current_trip = trip
        self.modifications.clear()
        self.ingr_list.clear()
        self.ingr_list.extend(trip.ingredients_needed)

        start, end = self.current_trip.date_range
        x = end - start
        self.duration_label.config(text=f"Trip covering meals for the next {x.days} days.")
        self.auto_sorter.refresh()

    def _autosorter_command(self, query: str, column: str, asc: bool):
        tv = self.shopping_list_disp.treeview
        if self.display_len > 0:
            tv.delete(*range(self.display_len))

        # was there an item already selected?
        selected_ingr = (
            self.ingr_list[self.editing_index]
            if self.editing_index is not None else None
        )

        key = {
            "ingr": lambda t: t[0].name,
            "qty": lambda t: t[1].magnitude
        }[column]

        self.ingr_list.sort(key=key, reverse=not asc)
        for i, (ingr, qty) in enumerate(self.ingr_list):
            tv.insert("", "end", id=i, text="", values=[ingr.name, ui.fmt_qty(qty)], tags=["cl"])

        if selected_ingr is not None:
            self.editing_index = self.ingr_list.index(selected_ingr)
            tv.selection_set(self.editing_index)
        self.display_len = len(self.ingr_list)

    def _on_double_click(self, tgt_str: str):
        self.shopping_list_disp.treeview.selection_set(tgt_str)
        self.focus_quantity_editor()

    def focus_quantity_editor(self):
        full_text = self.quantity_var.get()
        partial = full_text.lstrip()
        lhs = len(full_text) - len(partial)
        space_location = partial.rstrip().find(" ")
        if space_location == -1:
            space_location = tk.END
        self.quantity_editor.focus()
        self.quantity_editor.icursor(space_location)
        self.quantity_editor.selection_range(lhs, space_location)

    def _disable_qty_editor(self):
        self.quantity_editor.state(("disabled",))
        self.confirm_button.state(("disabled",))
        self.quantity_var.set("")
        self.confirm_button.config(text="Select an Ingredient")
        self.error_display.config(text="")

    def _enable_qty_editor(self):
        self.quantity_editor.state(("!disabled",))

    def _on_quantity_editor_return(self, event: tk.Event):
        if self.quantity_editor.instate(("!disabled",)) and self.confirm_button.instate(("!disabled",)):
            self.confirm_button.invoke()

    def _on_selection_update(self, event: tk.Event):
        selection = self.shopping_list_disp.treeview.selection()
        if len(selection) != 1:
            self.editing_index = None
            self._disable_qty_editor()
            return

        self._enable_qty_editor()

        ingr_index = int(selection[0])
        # Do nothing if the selected item is the same as the one being edited currently
        if ingr_index == self.editing_index:
            return
        ingr, qty = self.ingr_list[ingr_index]
        self.editing_index = ingr_index
        self.quantity_editor.delete(0, tk.END)
        self.quantity_editor.insert(tk.END, str(qty))

    def _on_quantity_text_update(self, *args):
        self.update_confirm_button()

    def update_confirm_button(self):
        if self.editing_index is None:
            return
        active_ingr, curr_qty = self.ingr_list[self.editing_index]
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
                command=lambda: self._update_active_ingr_qty(active_ingr.id, active_ingr.measurement_type.pint_unit * 0)
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
            new_qty = units.interpret_quantity(current_text, active_ingr.measurement_type.pint_unit)
        except Exception as e:
            set_mode_error(str(e))
            return
        
        # if user hasn't changed the quantity or the units for that quantity, the button should be disabled
        if new_qty == curr_qty and new_qty.units == curr_qty.units:
            set_mode_no_change()
            return

        set_mode_success(new_qty)

    def _update_active_ingr_qty(self, expected_id: int, new_quantity: pint.Quantity):
        assert self.editing_index is not None
        ingr, prev_qty = self.ingr_list[self.editing_index]
        assert ingr.id == expected_id
        assert ingr.measurement_type.pint_unit.is_compatible_with(new_quantity)

        self.ingr_list[self.editing_index] = ingr, new_quantity
        self.modifications[ingr] = new_quantity

        self.update_quantity_list()

    def update_quantity_list(self):
        self.auto_sorter.refresh()
        self.update_confirm_button()

def parse_duration_input(starting_point: dt.date, user_input: str) -> tuple[dt.date, dt.date] | ValueError | pint.PintError:
    user_input = user_input.strip()
    
    if not user_input:
        return starting_point, starting_point
    
    u = units.unit_reg
    try:
        duration = units.interpret_quantity(user_input, u.day)
    except (ValueError, pint.PintError) as e:
        return e
    return starting_point, starting_point + duration.to_timedelta()


DURATION_OPTIONS = [
    "1 day",
    *(f"{n} days" for n in range(2, 8)),
    "1 week",
    "2 weeks",
    "3 weeks",
    "1 month",
]