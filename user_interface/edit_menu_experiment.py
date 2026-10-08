from dataclasses import dataclass, field, InitVar
from tkinter import ttk
from tkinter import scrolledtext as scrtxt
import tkinter as tk

# add_event_menu, edit_event_menu = (generate_edit_menu(
#     [
#         ("Meal", "Foobar Salad", "db search options"),
#         ("Time", "10:52", "entry"),
#         ("Date", "9/30/26", "entry"),
#         ("Repeat", "Until stopping date", "fixed options"),
#         ("Interval", "Weekly", "fixed options"),
#         ("Stop on", "9/30/27", "entry"),
#     ],
#     ["Cancel", 1, save_button_name],
# ) for save_button_name in ["Create Event", "Update Event"])

class MenuField[T]:
    label: ttk.Label
    elem: T

class EventEditor:
    meal: MenuField[DbSearchOptions]
    time: MenuField[Entry]
    date: MenuField[Entry]
    repeat: MenuField[FixedOptions]
    interval: MenuField[FixedOptions]
    stop_on: MenuField[Entry]

@dataclass
class SharedData:
    container: InitVar[ttk.Frame]

    option_display_name: str

    def insert(self, row: int): pass

@dataclass(match_args=True, slots=True)
class Display(SharedData):
    display: ttk.Label = field(init=False)
    def __post_init__(self, container: ttk.Frame):
        self.display = ttk.Label(container)

    def insert(self, row: int):
        self.display.grid(row=row, column=1, sticky="nw")

    def set_text(self, text: str):
        self.display.config(text=text)

@dataclass(match_args=True, slots=True)
class Entry(SharedData):
    input_field: ttk.Entry = field(init=False)
    input_text: tk.StringVar = field(init=False)

    def __post_init__(self, container: ttk.Frame):
        self.input_field = ttk.Entry(container)
        self.input_text = tk.StringVar(self.input_field)
    
    def insert(self, row: int):
        self.input_field.grid(row=row, column=1, sticky="nw")
    
    def set_text(self, text: str):
        self.input_text.set(text)

    def get_text(self):
        return self.input_text.get()

@dataclass(match_args=True, slots=True)
class Button(SharedData):
    button_text: InitVar[str]

    button: ttk.Button = field(init=False)

    def __post_init__(self, container: ttk.Frame, button_text: str):
        self.button = ttk.Button(container, text=button_text)
    
    def insert(self, row: int):
        self.button.grid(row=row, column=1, sticky="nw")
    
    def set_text(self, text: str):
        self.button.config(text=text)

@dataclass(match_args=True, slots=True)
class Text(SharedData):
    input_field: scrtxt.ScrolledText = field(init=False)
    
    def __post_init__(self, container: ttk.Frame):
        self.input_field = scrtxt.ScrolledText(container, height=3)

    def insert(self, row: int):
        self.input_field.grid(row=row, column=1, sticky="nw")

    def clear_text(self):
        self.input_field.delete("0.0", tk.END)
    
    def set_text(self, text: str):
        self.clear_text()
        self.input_field.insert(tk.END, text)
    
    def get_text(self):
        return self.input_field.get("0.0", tk.END)

@dataclass(match_args=True, slots=True)
class FixedOptions(SharedData):
    pass

@dataclass(match_args=True, slots=True)
class DbSearchOptions(SharedData):
    pass

@dataclass(match_args=True, slots=True)
class Image(SharedData):
    pass

@dataclass(match_args=True, slots=True)
class ListDisplay(SharedData):
    pass

@dataclass(match_args=True, slots=True)
class Checkbox(SharedData):
    pass

@dataclass(match_args=True, slots=True)
class SeparatingBar:
    pass

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