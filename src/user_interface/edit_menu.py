from __future__ import annotations
from dataclasses import dataclass
from textwrap import wrap
from tkinter import ttk
from tkinter import scrolledtext as scrtxt
import tkinter as tk
from typing import Callable, Iterable, Protocol, override
import pint

from . import user_interface_impl as ui
from .treeview_utilities import ScrollableTreeview
from ..backend import units

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
    next_row: int
    menu_widgets: list[Validatable]
    submenus: list[EditMenu]

    def __init__(self, parent: tk.Misc) -> None:
        self.frame = ttk.Frame(parent, padding=10)
        self.frame.columnconfigure(1, minsize=10)
        self.next_row = 1
        self.menu_widgets = []
        self.submenus = []

    def insert[T: MenuWidget](self, name: str, elem: T) -> MenuField[T]:
        tgt_row = self.claim_row()
        field_label = ttk.Label(self.frame, text=name)
        field_label.grid(row=tgt_row, column=0, sticky="ne")
        elem.insert(row=tgt_row, column=2)
        menu_field = MenuField(field_label, elem)
        self.menu_widgets.append(menu_field.elem)
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

    def insert_spacer_row(self, height: int) -> int:
        spacer_row = self.claim_row()
        self.frame.rowconfigure(spacer_row, minsize=height)
        return spacer_row

    def register_submenu_for_checking(self, em: EditMenu):
        self.submenus.append(em)

    def check_all_input_and_show_errors(self) -> bool:
        """Return True if no errors, False otherwise."""
        success = True
        for w in self.menu_widgets:
            success = success and w.check_and_show_errors()
        for submenu in self.submenus:
            success = success and submenu.check_all_input_and_show_errors()
        return success
    
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
        self.search_display.heading("display", text="...")
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
        tgt_row = self.claim_row()
        field_label = ttk.Label(self.frame, text=name)
        field_label.grid(row=tgt_row, column=0, sticky="ne")
        elem.insert(row=tgt_row, column=2, search_menu=self)
        menu_field = MenuField(field_label, elem)
        self.menu_widgets.append(menu_field.elem)
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
    meal: MenuField[OpenDbSearchOptions]
    time: MenuField[Entry]
    date: MenuField[Entry]
    repeat: MenuField[FixedOptions]
    interval: MenuField[FixedOptions]
    stop_on: MenuField[Entry]

class Validatable:
    def check_and_show_errors(self) -> bool:
        """Return True if check was successful, False if errors."""
        return True

class MenuWidget(Validatable):
    def insert(self, row: int, column: int):
        raise NotImplementedError(f"`insert` not implemented for {type(self).__name__}")

class Searcher(Validatable):
    def insert(self, row: int, column: int, search_menu: EditMenuWithSearcher):
        raise NotImplementedError

    def notify_about_selection(self, index: int):
        raise NotImplementedError

class Display(MenuWidget):
    display: ttk.Label
    
    def __init__(self, container: ttk.Frame, initial_text: str):
        self.display = ttk.Label(container, text=initial_text)

    @override
    def insert(self, row: int, column: int):
        self.display.grid(row=row, column=column, sticky="nw")

    def set_text(self, text: str):
        self.display.config(text=text)

class InputCheck(Protocol):
    def identify_issues(self, text: str) -> str | None:
        """If nothing is wrong, return None, otherwise, return a string describing the problem."""
        raise NotImplementedError

@dataclass
class SimpleCheck(InputCheck):
    reason: str
    check: Callable[[str], bool]

    @override
    def identify_issues(self, text: str) -> str | None:
        return None if self.check(text) else self.reason

class Entry(MenuWidget):
    input_field: ttk.Entry

    def __init__(self, container: ttk.Frame, initial_text: str = ""):
        self.input_field = ttk.Entry(container)
        self.input_field.insert(tk.END, initial_text)

    def set_text(self, text: str):
        self.input_field.delete(0, tk.END)
        self.input_field.insert(tk.END, text)

    def get_text(self):
        return self.input_field.get()

    @override
    def insert(self, row: int, column: int):
        self.input_field.grid(row=row, column=column, sticky="nw")

class CheckedEntry(MenuWidget):
    input_check: InputCheck
    error_visible: bool

    frame: ttk.Frame
    error_label: ttk.Label
    input_field: ttk.Entry
    input_var: tk.StringVar

    def __init__(self, container: ttk.Frame, input_check: InputCheck, initial_text: str = ""):
        self.input_check = input_check
        self.error_visible = False

        self.frame = ttk.Frame(container)
        self.error_label = ttk.Label(self.frame)
        self.input_field = ttk.Entry(self.frame)
        self.input_var = tk.StringVar(self.input_field)

        # self.frame.columnconfigure(0, weight=1)
        self.input_field.grid(row=0, column=0, sticky="w")
        self.error_label.grid(row=0, column=1, sticky="w")

        self.input_field.config(textvariable=self.input_var)
        self.input_field.insert(tk.END, initial_text)

        # self.input_var.trace_add("write", self._on_edit)

    # def _on_edit(self, *_):
    #     if not self.error_visible:
    #         return
    #     self.error_label.config

    def set_text(self, text: str):
        self.input_field.delete(0, tk.END)
        self.input_field.insert(tk.END, text)

    def get_text(self):
        return self.input_field.get()

    @override
    def check_and_show_errors(self) -> bool:
        result = self.input_check.identify_issues(self.get_text())
        if result is None:
            self.error_label.config(text="")
            return True
        else:
            self.error_visible = True
            self.error_label.config(text=result)
            return False

    @override
    def insert(self, row: int, column: int):
        self.frame.grid(row=row, column=column, sticky="nw")

class Button(MenuWidget):
    button: ttk.Button

    def __init__(self, container: ttk.Frame, button_text: str):
        self.button = ttk.Button(container, text=button_text)
    
    @override
    def insert(self, row: int, column: int):
        self.button.grid(row=row, column=column, sticky="nw")
    
    def set_text(self, text: str):
        self.button.config(text=text)


class Text(MenuWidget):
    input_field: scrtxt.ScrolledText
    
    def __init__(self, container: ttk.Frame, initial_text: str = ""):
        self.input_field = scrtxt.ScrolledText(container, height=3)
        current_entry_font = ttk.Style().lookup("TEntry", "font")
        if current_entry_font is not None:
            self.input_field.config(font=current_entry_font)
        self.input_field.insert(tk.END, initial_text)

        # method
        self.direct_grid = self.input_field.grid

    @override
    def insert(self, row: int, column: int):
        self.input_field.grid(row=row, column=column, sticky="nw")

    def clear_text(self):
        self.input_field.delete("0.0", tk.END)
    
    def set_text(self, text: str):
        self.clear_text()
        self.input_field.insert(tk.END, text)
    
    def get_text(self):
        return self.input_field.get("0.0", tk.END).removesuffix("\n")


class QuantityEntry(MenuWidget):
    frame: ttk.Frame
    input_field: ttk.Entry
    error_label: ttk.Label
    input_var: tk.StringVar

    _unit_constraint: pint.Unit | None

    def __init__(self, container: ttk.Frame, quantity: pint.Quantity, unit_constraint: pint.Unit | None):
        self._unit_constraint = unit_constraint

        self.frame = ttk.Frame(container)
        self.input_field = ttk.Entry(self.frame, width=30)
        self.error_label = ttk.Label(self.frame, anchor="w", wraplength=self.input_field.winfo_reqwidth())

        self.input_field.grid(row=0, column=0, sticky="nw")
        self.error_label.grid(row=1, column=0, sticky="nwe")
        
        self.input_var = tk.StringVar(self.input_field)
        self.input_field.config(textvariable=self.input_var)
        self.input_var.trace_add("write", self._on_text_update)
        self.input_field.insert(tk.END, ui.fmt_qty(quantity))

    def set_unit_constraint(self, new_unit_constraint: pint.Unit | None):
        self._unit_constraint = new_unit_constraint

        # refresh error display based on new unit_constraint
        self._on_text_update()
    
    @override
    def insert(self, row: int, column: int):
        self.frame.grid(row=row, column=column, sticky="nw")

    @override
    def check_and_show_errors(self) -> bool:
        try:
            self.get_quantity()
            return True
        except Exception:
            return False
    
    def set_text(self, text: str):
        self.input_field.delete(0, tk.END)
        self.input_field.insert(tk.END, text)
    
    def get_text(self):
        return self.input_field.get()

    def get_quantity(self) -> pint.Quantity:
        """Raises an exception on invalid input"""
        text = self.get_text().strip() or "0" # interpret empty input as zero?
        parsed = units.interpret_quantity(text, self._unit_constraint)
        return parsed

    def _on_text_update(self, *_):
        try:
            self.error_label.config(text=f"= {ui.fmt_qty(self.get_quantity())}")
        except Exception as err:
            self.error_label.config(text=str(err))

def identity(n): return n

class FixedOptions(MenuWidget):
    def __init__(self, container: ttk.Frame): pass

class OpenDbSearchOptions(Searcher):
    search_bar: ttk.Entry
    text_var: tk.StringVar
    search_fn: Callable[[str], list[str]]
    display_header: str
    entries: list[str]

    search_menu: EditMenuWithSearcher

    _update_on_text_changes: bool

    def __init__(self, container: ttk.Frame, display_header: str, db_search: Callable[[str], list[str]], initial_value: str = ""):
        self.search_bar = ttk.Entry(container)
        self.text_var = tk.StringVar(self.search_bar)
        self.search_fn = db_search
        self.display_header = display_header
        self.entries = []

        # self.search_menu is set when self.insert is called

        self.search_bar.config(textvariable=self.text_var)
        self.search_bar.insert(tk.END, initial_value)
        self.text_var.trace_add("write", self._on_text_update)
        self.search_bar.bind("<FocusIn>", self._on_focus, add=True)
        self.search_bar.bind("<KeyPress-Return>", self._on_press_enter, add=True)
        self._update_on_text_changes = True

    def _on_press_enter(self, event: tk.Event):
        if len(self.entries) == 1:
            self.search_menu.set_selected(0)
            self.search_bar.after_idle(self.search_bar.icursor, tk.END)
    
    def _on_focus(self, event: tk.Event):
        self.show_search_results_in_side_bar()

    def _on_text_update(self, *_):
        if self._update_on_text_changes:
            self.selected = None
            self.show_search_results_in_side_bar()

    @override
    def insert(self, row: int, column: int, search_menu: EditMenuWithSearcher):
        self.search_menu = search_menu
        self.search_bar.grid(row=row, column=column, sticky="nw")

    def set_text(self, text: str, update_search_results=True):
        if not update_search_results:
            self._update_on_text_changes = False
        self.text_var.set(text)
        if not update_search_results:
            self._update_on_text_changes = True

    def get_text(self) -> str:
        return self.text_var.get()

    def show_search_results_in_side_bar(self):
        raw_text = self.get_text()
        search_text = raw_text.strip()
        self.entries = results = self.search_fn(search_text)
        self.search_menu.post_search(self, self.display_header, results)

        if len(results) == 1 and results[0] == raw_text:
            self.search_menu.set_selected(0)

    def notify_about_selection(self, index: int):
        self.set_text(self.entries[index], update_search_results=False)

class ClosedDbSearchOptions[T](Searcher):
    search_bar: ttk.Entry
    text_var: tk.StringVar
    search_fn: Callable[[str], list[T]]
    translation_fn: Callable[[T], str]
    display_header: str
    error_msg: str
    entries: list[T]
    selected: T | None


    search_menu: EditMenuWithSearcher

    _update_on_text_changes: bool
    
    def __init__(
            self,
            container: ttk.Frame,
            display_header: str,
            error_msg: str,
            db_search: Callable[[str], list[T]],
            translation_fn: Callable[[T], str],
            initial_value: T | None = None,
            selection_callback: Callable[[T | None], None] | None = None
            ) -> None:
        initial_value_str = translation_fn(initial_value) if initial_value is not None else ""

        self.frame = ttk.Frame(container)

        self.error_label = ttk.Label(self.frame)
        self.error_label.grid(row=0, column=1)

        self.search_bar = ttk.Entry(self.frame)
        self.text_var = tk.StringVar(self.search_bar)
        self.search_bar.grid(row=0, column=0)
        
        self.search_fn = db_search
        self.translation_fn = translation_fn
        self.display_header = display_header
        self.error_msg = error_msg
        self.entries = []
        # self.search_menu is set when self.insert is called
        self.selected = initial_value
    
        self.search_bar.config(textvariable=self.text_var)
        self.search_bar.insert(tk.END, initial_value_str)
        self.text_var.trace_add("write", self._on_text_update)
        self.search_bar.bind("<FocusIn>", self._on_focus, add=True)
        self.search_bar.bind("<KeyPress-Return>", self._on_press_enter, add=True)

        self._update_on_text_changes = True
        self._selection_callback = selection_callback

    @override
    def check_and_show_errors(self) -> bool:
        if self.get_selection() is not None:
            self.error_label.config(text="")
            return True
        else:
            # self.error_visible = True
            self.error_label.config(text=self.error_msg)
            return False
    
    def _on_press_enter(self, event: tk.Event):
        if len(self.entries) == 1:
            self.search_menu.set_selected(0)
            self.search_bar.after_idle(self.search_bar.icursor, tk.END)
    
    def _on_focus(self, event: tk.Event):
        self.show_search_results_in_side_bar()
    
    def _on_text_update(self, *_):
        if self._update_on_text_changes:
            self.selected = None
            self.show_search_results_in_side_bar()
    
    @override
    def insert(self, row: int, column: int, search_menu: EditMenuWithSearcher):
        self.search_menu = search_menu
        self.frame.grid(row=row, column=column, sticky="nw")
    
    def set_text(self, text: str, update_search_results=True):
        if not update_search_results:
            self._update_on_text_changes = False
        self.text_var.set(text)
        if not update_search_results:
            self._update_on_text_changes = True
    
    def get_text(self) -> str:
        return self.text_var.get()
    
    def get_selection(self) -> T | None:
        return self.selected
    
    def show_search_results_in_side_bar(self):
        search_text = self.get_text().strip()
        self.entries = self.search_fn(search_text)
        self.search_menu.post_search(self, self.display_header, list(map(self.translation_fn, self.entries)))
    
        if len(self.entries) == 1 and self.translation_fn(self.entries[0]).strip().lower() == search_text.lower():
            self.search_menu.set_selected(0)
    
    def notify_about_selection(self, index: int):
        self.selected = self.entries[index]
        self.set_text(self.translation_fn(self.selected) , update_search_results=False)
        if self._selection_callback is not None:
            self._selection_callback(self.selected)

x: ClosedDbSearchOptions[int]

class Image(MenuWidget):
    image: ttk.Label

    def __init__(self, container: ttk.Frame):
        self.image = ttk.Label(container, image=ui.placeholder_image, padding=2, relief=tk.RIDGE)
    
    @override
    def insert(self, row: int, column: int):
        self.image.grid(row=row, column=column, sticky="nw")

class ListDisplay(MenuWidget):
    def __init__(self, container: ttk.Frame): pass

class Checkbox(MenuWidget):
    def __init__(self, container: ttk.Frame): pass

class SeparatingBar:
    def __init__(self, container: ttk.Frame): pass
