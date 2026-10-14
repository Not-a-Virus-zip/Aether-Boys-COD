from dataclasses import dataclass
from tkinter import ttk
from tkinter import scrolledtext as scrtxt
import tkinter as tk
from typing import Callable, Iterable
import pint

from . import user_interface_impl as ui

from ..backend.units import units

def show_edit_menu(root: tk.Tk | tk.Toplevel, name: str, edit_frame_maker: Callable[[tk.Toplevel], ttk.Frame]):
    edit_menu = tk.Toplevel(root)
    edit_menu.wm_title(name)
    edit_menu.grid_propagate(True)
    edit_frame = edit_frame_maker(edit_menu)
    edit_menu.columnconfigure(0, weight=1)
    edit_menu.rowconfigure(0, weight=1)
    edit_frame.grid(row=0, column=0, sticky="nsew")
    edit_menu.focus()

@dataclass(slots=True)
class MenuField[T]:
    label: ttk.Label
    elem: T

class EditMenu:
    def __init__(self, parent: tk.Toplevel) -> None:
        self.frame = ttk.Frame(parent, padding=10)
        # self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(1, minsize=10)
        self.next_row = 1

    def insert[T: SharedData](self, name: str, elem: T) -> MenuField[T]:
        field_label = ttk.Label(self.frame, text=name)
        field_label.grid(row=self.next_row, column=0, sticky="ne")
        elem.insert(row=self.next_row, column=2)
        menu_field = MenuField(field_label, elem)
        self.next_row += 1
        return menu_field

    def finish_construction(self, bottom_buttons: Iterable[tuple[str, Callable[[], None]] | str | int]) -> list[ttk.Button]:
        finish_row = self.next_row
        in_between_row = self.next_row + 1
        bottom_buttons_row = self.next_row + 2
        self.next_row += 3
        self.frame.rowconfigure(finish_row, weight=1)
        self.frame.rowconfigure(in_between_row, minsize=10)
        bottom_buttons_frame, buttons = ui.make_buttons(self.frame, bottom_buttons)
        bottom_buttons_frame.grid(column=0, row=bottom_buttons_row, columnspan=4, sticky="ew")
        return buttons

    def get_row_count(self) -> int:
        return self.next_row


class EventEditor:
    """EXAMPLE CASE"""
    meal: MenuField[DbSearchOptions]
    time: MenuField[Entry]
    date: MenuField[Entry]
    repeat: MenuField[FixedOptions]
    interval: MenuField[FixedOptions]
    stop_on: MenuField[Entry]


class SharedData:
    def insert(self, row: int, column: int): pass


class Display(SharedData):
    display: ttk.Label
    def __init__(self, container: ttk.Frame, initial_text: str):
        self.display = ttk.Label(container, text=initial_text)

    def insert(self, row: int, column: int):
        self.display.grid(row=row, column=column, sticky="nw")

    def set_text(self, text: str):
        self.display.config(text=text)


class Entry(SharedData):
    input_field: ttk.Entry

    def __init__(self, container: ttk.Frame, initial_text: str = ""):
        self.input_field = ttk.Entry(container)
        self.input_field.insert(tk.END, initial_text)
    
    def insert(self, row: int, column: int):
        self.input_field.grid(row=row, column=column, sticky="nw")
    
    def set_text(self, text: str):
        self.input_field.delete(0, tk.END)
        self.input_field.insert(tk.END, text)

    def get_text(self):
        return self.input_field.get()


class Button(SharedData):
    button: ttk.Button

    def __init__(self, container: ttk.Frame, button_text: str):
        self.button = ttk.Button(container, text=button_text)
    
    def insert(self, row: int, column: int):
        self.button.grid(row=row, column=column, sticky="nw")
    
    def set_text(self, text: str):
        self.button.config(text=text)


class Text(SharedData):
    input_field: scrtxt.ScrolledText
    
    def __init__(self, container: ttk.Frame):
        self.input_field = scrtxt.ScrolledText(container, height=3)

    def insert(self, row: int, column: int):
        self.input_field.grid(row=row, column=column, sticky="nw")

    def clear_text(self):
        self.input_field.delete("0.0", tk.END)
    
    def set_text(self, text: str):
        self.clear_text()
        self.input_field.insert(tk.END, text)
    
    def get_text(self):
        return self.input_field.get("0.0", tk.END)


class QuantityEntry(SharedData):
    input_field: ttk.Entry
    def __init__(self, container: ttk.Frame, quantity: pint.Quantity):
        self.input_field = ttk.Entry(container)
        self.input_field.insert(tk.END, ui.fmt_qty(quantity))
    
    def insert(self, row: int, column: int):
        self.input_field.grid(row=row, column=column, sticky="nw")
    
    def set_text(self, text: str):
        self.input_field.delete(0, tk.END)
        self.input_field.insert(tk.END, text)
    
    def get_text(self):
        return self.input_field.get()

    def get_quantity(self) -> pint.Quantity:
        parsed = units.parse_expression(self.get_text())
        return parsed


class FixedOptions(SharedData):
    def __init__(self, container: ttk.Frame): pass

class DbSearchOptions[T](SharedData):
    search_bar: ttk.Entry
    text_var: tk.StringVar
    side_bar_ref: ttk.Treeview
    search_fn: Callable[[str], list[T]]
    translation_fn: Callable[[T], str]
    display_header: str
    entries: list[T]
    selected: T | None

    def __init__(self, container: ttk.Frame, side_bar: ttk.Treeview, initial_value: str, db_search: Callable[[str], list[T]], translation_fn: Callable[[T], str], display_header: str = "Options"):
        self.search_bar = ttk.Entry(container)
        self.text_var = tk.StringVar(self.search_bar)
        self.side_bar_ref = side_bar
        self.search_fn = db_search
        self.translation_fn = translation_fn
        self.display_header = display_header
        self.entries = []
        self.selected = None

        self.search_bar.config(textvariable=self.text_var)
        self.search_bar.insert(tk.END, initial_value)
        self.text_var.trace_add("write", self._on_text_update)
        self.search_bar.bind("<FocusIn>", self._on_focus)
        self.update_on_text_changes = True

    def insert(self, row: int, column: int):
        self.search_bar.grid(row=row, column=column, sticky="nw")

    def set_text(self, text: str):
        self.text_var.set(text)

    def get_text(self) -> str:
        return self.text_var.get()

    def get_selection(self) -> T | None:
        return self.selected

    def show_search_results_in_side_bar(self):
        self.side_bar_ref.state(("!disabled",))
        self.side_bar_ref.bind("<<TreeviewSelect>>", self._on_select_search_results)
        self.side_bar_ref.delete(*self.side_bar_ref.get_children())
        self.entries = self.search_fn(self.text_var.get())
        if not self.entries:
            self.side_bar_ref.config(selectmode=tk.NONE)
            self.side_bar_ref.column("display", anchor=tk.CENTER)
            self.side_bar_ref.insert("", "end", id=0, text="", values=["... No Results found ..."])
        else:
            self.side_bar_ref.column("display", anchor=tk.W)
            self.side_bar_ref.config(selectmode=tk.BROWSE)
            for i, entry in enumerate(self.entries):
                self.side_bar_ref.insert("", "end", id=i, text="", values=[self.translation_fn(entry)])
        self.side_bar_ref.heading("display", text=self.display_header)

    def _on_select_search_results(self, event: tk.Event):
        selected = self.side_bar_ref.selection()
        if len(selected) >= 1:
            selected_index = int(selected[0])
            self.selected = self.entries[selected_index]
            self.update_on_text_changes = False
            self.set_text(self.translation_fn(self.selected))
            self.update_on_text_changes = True

    def _on_focus(self, event: tk.Event):
        self.show_search_results_in_side_bar()

    def _on_text_update(self, *_):
        if self.update_on_text_changes:
            self.show_search_results_in_side_bar()
            self.selected = None

class Image(SharedData):
    def __init__(self, container: ttk.Frame): pass

class ListDisplay(SharedData):
    def __init__(self, container: ttk.Frame): pass

class Checkbox(SharedData):
    def __init__(self, container: ttk.Frame): pass

class SeparatingBar:
    def __init__(self, container: ttk.Frame): pass

"""
match option_type:
    case "display":
        display = ttk.Label(holder, text=sample_input)
        display.grid(row=i, column=1, sticky="nw")
    case "entry":
        entry = ttk.Entry(holder)
        entry.insert(tk.END, sample_input)
        entry.grid(row=i, column=1, sticky="nw")
    case "button":
        button = ttk.Button(holder, text=sample_input)
        button.grid(row=i, column=1, sticky="nw")
    case "add ingredient":
        ing_name, quantity = sample_input.split(",")
        add_frame = ttk.Frame(holder)

        db_ing_search = ttk.Combobox(add_frame, values=[ing_name])
        db_ing_search.insert(tk.END, ing_name)
        db_ing_search.grid(row=0, column=0)

        qty_entry = ttk.Entry(add_frame)
        qty_entry.insert(tk.END, quantity)
        qty_entry.grid(row=0, column=1)

        add_button = ttk.Button(add_frame, text="Add")
        add_button.grid(row=0, column=2)

        add_frame.columnconfigure(3, weight=1)

        remove_button = ttk.Button(add_frame, text="Remove")
        remove_button.grid(row=0, column=3, sticky="e")

        add_frame.grid(row=i, column=1, sticky="nw")
    case "text":
        text = ScrolledText(holder, height=3)
        text.insert(tk.END, sample_input)
        text.grid(row=i, column=1, sticky="new")
    case "fixed options":
        opt_var = tk.StringVar(holder, value=sample_input)
        fixed_opt = ttk.OptionMenu(holder, opt_var, sample_input)
        fixed_opt.grid(row=i, column=1, sticky="nw")
    case "db search options":
        db_search = ttk.Combobox(holder, values=[sample_input])
        db_search.insert(tk.END, sample_input)
        db_search.grid(row=i, column=1, sticky="nw")
    case "list display":
        db_list_frame = ttk.Frame(holder)
        header, *data = sample_input.splitlines()
        headers = header.split()
        header_ids = list(map(str.lower, headers))
        list_display = ttk.Treeview(db_list_frame, columns=header_ids, show="headings")
        for name, hid in zip(headers, header_ids):
            list_display.heading(hid, text=name)
        for line in data:
            list_display.insert("", "end", values=line.split(","))
        scrollbar = ttk.Scrollbar(db_list_frame, command=list_display.yview)

        # db_list_frame.columnconfigure(0, weight=1)
        list_display.grid(row=0, column=0)
        scrollbar.grid(row=0, column=1, sticky="ns")

        list_display.config(yscrollcommand=scrollbar.set)

        db_list_frame.grid(row=i, column=1, sticky="nw")
    case "image":
        image = ttk.Label(holder, image=placeholder_image, padding=2, relief=tk.RIDGE)
        image.grid(row=i, column=1, sticky="nw")
    case "checkbox":
        checkbox = ttk.Checkbutton(holder)
        checkbox.invoke()
        checkbox.grid(row=i, column=1, sticky="nw")
    case "separating bar":
        bar = ttk.Separator(holder)
        bar.grid(row=i, column=0, columnspan=2, sticky="ew")
        continue
"""
