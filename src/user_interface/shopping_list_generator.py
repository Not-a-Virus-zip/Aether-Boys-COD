from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import datetime as dt

import pint

from ..backend import units
from .treeview_tools import ScrollableTreeview
from . import (
    user_interface_impl as ui,
    calendar as cal,
)

class ShoppingListGeneratorUI:
    name: str = "Your Shopping List"

    def __init__(self, parent: ttk.Notebook, backend: ui.Backend):
        self.frame = ttk.Frame(parent, name="shopping", padding=20)

        self.backend = backend

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

        self.shopping_list_disp.grid(row=1, column=0, columnspan=2, sticky="news")
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        b_frame, (self.print_button, self.save_to_file_button) = ui.make_buttons(
            self.frame,
            (
                "Print",
                "Save to File"
            ),
            button_weight=1,
        )
        b_frame.grid(row=2, column=0, columnspan=2)

        # default duration is 1 week
        duration_entry.current(7)

    def _on_duration_modified(self, *_):
        user_input = self.duration_var.get()
        match parse_duration_input(dt.date.today(), user_input):
            case Exception() as e:
                self.duration_error_label.config(text=str(e))
            case span:
                self.update_shopping_preview(span)
    
    def update_shopping_preview(self, span: tuple[dt.date, dt.date]):
        prev_len = 0 if self.shopping_list is None else len(self.shopping_list.ingredients_needed)
        
        tv = self.shopping_list_disp.treeview
        if prev_len > 0:
            tv.delete(*range(prev_len))

        self.shopping_list = self.backend.generator.get_needed_ingredients(*span)

        for i, (ingr, qty) in enumerate(self.shopping_list.ingredients_needed):
            self.shopping_list_disp.treeview.insert("", "end", id=i, text="", values=[ingr.name, ui.fmt_qty(qty)])

def parse_duration_input(starting_point: dt.date, user_input: str) -> tuple[dt.date, dt.date] | ValueError | pint.UndefinedUnitError:
    user_input = user_input.strip()
    
    if not user_input:
        return starting_point, starting_point
    
    u = units.unit_reg
    try:
        duration = units.interpret_quantity(user_input, u.day)
    except (ValueError, pint.UndefinedUnitError) as e:
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