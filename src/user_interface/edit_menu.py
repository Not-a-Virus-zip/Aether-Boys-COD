from __future__ import annotations
from dataclasses import dataclass
from tkinter import ttk
from tkinter import scrolledtext as scrtxt
import tkinter as tk
from typing import Callable, Iterable
import pint

from . import user_interface_impl as ui
from .treeview_utilities import ScrollableTreeview
from ..backend.units import units

def show_edit_menu(root: tk.Tk | tk.Toplevel, name: str, edit_frame_maker: Callable[[tk.Toplevel], ttk.Frame]):
    edit_menu = tk.Toplevel(root)
    edit_menu.wm_title(name)
    edit_menu.grid_propagate(True)
    edit_frame = edit_frame_maker(edit_menu)
    edit_menu.columnconfigure(0, weight=1)
    edit_menu.rowconfigure(0, weight=1)
    edit_frame.grid(row=0, column=0, sticky="nsew")
    edit_menu.resizable(False, False)
    edit_menu.focus()

@dataclass(slots=True)
class MenuField[T]:
    label: ttk.Label
    elem: T

class EditMenu:
    """
    A base class used to partially automate the construction of pop-up menus.
    To use, call `insert` to add elements to the menu.
    Call `finish_construction` once all elements have been added.
    It also lets you add save/cancel buttons to the bottom of the menu.
    """
    frame: ttk.Frame

    def __init__(self, parent: tk.Misc) -> None:
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.columnconfigure(1, minsize=10)
        self.next_row = 1

    def insert[T: SharedData](self, name: str, elem: T) -> MenuField[T]:
        tgt_row = self.claim_row()
        field_label = ttk.Label(self.frame, text=name)
        field_label.grid(row=tgt_row, column=0, sticky="ne")
        elem.insert(row=tgt_row, column=2)
        menu_field = MenuField(field_label, elem)

        return menu_field

    def finish_construction(self, bottom_buttons: Iterable[tuple[str, Callable[[], None]] | str | int]) -> list[ttk.Button]:
        """Add buttons at the bottom of the page (optional)"""
        self.frame.rowconfigure(self.claim_row(), weight=1)
        self.frame.rowconfigure(self.claim_row(), minsize=10)
        bottom_buttons_frame, buttons = ui.make_buttons(self.frame, bottom_buttons)
        bottom_buttons_frame.grid(column=0, row=self.claim_row(), columnspan=5, sticky="ew")
        return buttons

    def claim_row(self) -> int:
        """Reserve the next unclaimed row for use in the UI"""
        claimed_row = self.next_row
        self.next_row += 1
        return claimed_row
    
    def get_row_count(self) -> int:
        return self.next_row

    def add_empty_rows(self, how_many: int):
        self.next_row += how_many

class EditMenuWithSearcher(EditMenu):
    """
    An extension of EditMenu which has a panel on the side which shows
    live search results (required for DbSearchOptions).
    """
    search_display: ttk.Treeview
    active_searcher: Searcher | None

    def __init__(self, parent: tk.Toplevel) -> None:
        super().__init__(parent)
        self.frame.columnconfigure(3, minsize=10)
        self.search_display = ttk.Treeview(self.frame, columns=["display"], show="headings")
        self.db_search_scrollbar = ttk.Scrollbar(self.frame, command=self.search_display.yview)
        self.search_display.config(yscrollcommand=self.db_search_scrollbar.set)
        self.search_display.state(("disabled",))

        self.search_display.bind("<<TreeviewSelect>>", self._on_select_search_result)

    def finish_construction(self, bottom_buttons: Iterable[tuple[str, Callable[[], None]] | str | int]) -> list[ttk.Button]:
        buttons = super().finish_construction(bottom_buttons)
        row_count = self.get_row_count()
        self.search_display.grid(row=1, column=4, rowspan=row_count - 3, sticky="ns")
        self.db_search_scrollbar.grid(row=1, column=5, rowspan=row_count - 3, sticky="ns")
        return buttons

    def _on_select_search_result(self, event: tk.Event):
        selected = self.search_display.selection()
        if len(selected) >= 1:
            assert self.active_searcher is not None
            selected_index = int(selected[0])
            self.active_searcher.notify_about_selection(selected_index)

    def insert_searcher[T: Searcher](self, name: str, elem: T) -> MenuField[T]:
        field_label = ttk.Label(self.frame, text=name)
        field_label.grid(row=self.next_row, column=0, sticky="ne")
        elem.insert(row=self.next_row, column=2, search_menu=self)
        menu_field = MenuField(field_label, elem)
        self.next_row += 1
        return menu_field

    def post_search(self, menu: Searcher, display_header: str, values: list[str]):
        self.active_searcher = menu
        self.search_display.state(("!disabled",))
        self.search_display.delete(*self.search_display.get_children())
        if not values:
            self.search_display.config(selectmode=tk.NONE)
            self.search_display.column("display", anchor=tk.CENTER)
            self.search_display.insert("", "end", id=0, text="", values=["... No Results found ..."])
        else:
            self.search_display.column("display", anchor=tk.W)
            self.search_display.config(selectmode=tk.BROWSE)
            for i, entry in enumerate(values):
                self.search_display.insert("", "end", id=i, text="", values=[entry])
        self.search_display.heading("display", text=display_header)

    def set_selected(self, index: int):
        assert self.active_searcher is not None
        self.search_display.selection_set(index)


class EventEditor:
    """EXAMPLE CASE"""
    meal: MenuField[DbSearchOptions]
    time: MenuField[Entry]
    date: MenuField[Entry]
    repeat: MenuField[FixedOptions]
    interval: MenuField[FixedOptions]
    stop_on: MenuField[Entry]


class SharedData:
    def insert(self, row: int, column: int):
        raise NotImplementedError(f"`insert` not implemented for {type(self).__name__}")

class Searcher:
    def insert(self, row: int, column: int, search_menu: EditMenuWithSearcher):
        raise NotImplementedError

    def notify_about_selection(self, index: int):
        raise NotImplementedError

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
    
    def __init__(self, container: ttk.Frame, initial_text: str = ""):
        self.input_field = scrtxt.ScrolledText(container, height=3)
        current_entry_font = ttk.Style().lookup("TEntry", "font")
        if current_entry_font is not None:
            self.input_field.config(font=current_entry_font)
        self.input_field.insert(tk.END, initial_text)

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

def identity(n): return n

class FixedOptions(SharedData):
    def __init__(self, container: ttk.Frame): pass

class DbSearchOptions[T](Searcher):
    search_bar: ttk.Entry
    text_var: tk.StringVar
    search_fn: Callable[[str], list[T]]
    translation_fn: Callable[[T], str]
    display_header: str
    entries: list[T]
    search_menu: EditMenuWithSearcher
    selected: T | None

    def __init__(self, container: ttk.Frame, display_header: str, db_search: Callable[[str], list[T]], translation_fn: Callable[[T], str] = identity, initial_value: str = ""):
        self.search_bar = ttk.Entry(container)
        self.text_var = tk.StringVar(self.search_bar)
        self.search_fn = db_search
        self.translation_fn = translation_fn
        self.display_header = display_header
        self.entries = []
        # self.search_menu is set when self.insert is called
        self.selected = None

        self.search_bar.config(textvariable=self.text_var)
        self.search_bar.insert(tk.END, initial_value)
        self.text_var.trace_add("write", self._on_text_update)
        self.search_bar.bind("<FocusIn>", self._on_focus, add=True)
        self.search_bar.bind("<KeyPress-Return>", self._on_press_enter, add=True)
        self.update_on_text_changes = True

    def _on_press_enter(self, event: tk.Event):
        if len(self.entries) == 1:
            self.search_menu.set_selected(0)
            self.search_bar.after_idle(self.search_bar.icursor, tk.END)
    
    def _on_focus(self, event: tk.Event):
        self.show_search_results_in_side_bar()

    def _on_text_update(self, *_):
        if self.update_on_text_changes:
            self.selected = None
            self.show_search_results_in_side_bar()

    def insert(self, row: int, column: int, search_menu: EditMenuWithSearcher):
        self.search_menu = search_menu
        self.search_bar.grid(row=row, column=column, sticky="nw")

    def set_text(self, text: str, skip_text_update_callback=False):
        if skip_text_update_callback:
            self.update_on_text_changes = False
        self.text_var.set(text)
        if skip_text_update_callback:
            self.update_on_text_changes = True

    def get_text(self) -> str:
        return self.text_var.get()

    def get_selection(self) -> T | None:
        return self.selected

    def show_search_results_in_side_bar(self):
        search_text = self.text_var.get().strip()
        self.entries = self.search_fn(search_text)
        self.search_menu.post_search(self, self.display_header, list(map(self.translation_fn, self.entries)))

        if len(self.entries) == 1 and self.translation_fn(self.entries[0]).strip().lower() == search_text.lower():
            self.search_menu.set_selected(0)

    def notify_about_selection(self, index: int):
        self.selected = self.entries[index]
        self.set_text(self.translation_fn(self.selected), skip_text_update_callback=True)

class Image(SharedData):
    image: ttk.Label

    def __init__(self, container: ttk.Frame):
        self.image = ttk.Label(container, image=ui.placeholder_image, padding=2, relief=tk.RIDGE)
    
    def insert(self, row: int, column: int):
        self.image.grid(row=row, column=column, sticky="nw")


class IngredientSelector(SharedData):
    ingredient_list: ScrollableTreeview
    def __init__(self, container: ttk.Frame, initial_data: tuple):
        self.frame = ttk.Frame(container)
        self.ingredient_list = ScrollableTreeview(self.frame, columns=("name", "qty"), show="headings", selectmode="browse")

        tv = self.ingredient_list.treeview
        tv.heading("name", text="Name")
        tv.column("name", anchor="w", width=1)
        tv.heading("qty", text="Quantity")
        tv.column("qty", anchor="e", width=1)

        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.ingredient_list.grid(row=0, column=0, sticky="news")

    def insert(self, row: int, column: int):
        self.frame.grid(row=row, column=column, sticky="news")

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
