import random
from typing import Literal, Callable, Iterable
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import tkinter as tk
from dataclasses import dataclass
import enum

import pint

from . import (
    edit_menu as em,
    virtual_pantry as vp,
    ingredients_list as il,
)
import dummy_business_logic_api as bl



def fmt_qty(qty: pint.Quantity | pint.Unit) -> str:
    return f"{qty:~P}"

def test_ui():
    app = Application()

    global placeholder_image
    placeholder_image = tk.PhotoImage(file="src/user_interface/placeholder.png")
    app.run()

class Application:
    root: tk.Tk
    interface: "UserInterface"

    def __init__(self):
        self.root = tk.Tk()
        self.root.wm_title("Meal Planner")
        self.root.geometry("550x400")
        self.logic = bl.BusinessLogic()
        self.interface = UserInterface(self.root, self.logic)

    def run(self):
        self.root.mainloop()

class UserInterface:
    def __init__(self, root: tk.Tk, logic: bl.BusinessLogic):
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        alternate_header = ttk.Notebook(root)
        self.contents = (
            self.pantry,
            self.meals,
            self.calendar,
            self.shopping_list,
            self.ingredients,
            self.settings,
        ) = (
            vp.VirtualPantry(root, logic),
            make_meal_catalogue(root),
            make_calendar(root, DayOfTheWeek.Saturday, 30),
            make_shopping_list(root),
            il.IngredientsList(root, logic),
            make_settings(root),
        )

        for thing in self.contents:
            alternate_header.add(thing.frame, text=thing.name, state=tk.DISABLED)
        for pane in [".ingredients", ".virtual pantry"]:
            alternate_header.tab(pane, state=tk.NORMAL)
        alternate_header.select(".ingredients")
        alternate_header.grid(row=0, column=0, sticky="nsew")

def show_click(info):
    return lambda: messagebox.showinfo("This is a Button", f"You have clicked '{info}'.")

def make_buttons(put_in: tk.Misc, button_instructions: Iterable[tuple[str, Callable[[], None]] | str | int], button_weight: int | None = None) -> tuple[ttk.Frame, list[ttk.Button]]:
    bottom_buttons_frame = ttk.Frame(put_in)
    buttons = []

    def generate_button(name: str, command=None):
        button = ttk.Button(bottom_buttons_frame, text=name)
        if command is not None:
            button.config(command=command)
        if button_weight is not None and button_weight > 0:
            bottom_buttons_frame.columnconfigure(i, weight=button_weight)
            button.grid(row=0, column=i, sticky="ew")
        else:
            button.grid(row=0, column=i)
        buttons.append(button)

    for i, slot in enumerate(button_instructions):
        match slot:
            case str(name):
                generate_button(name)
            case str(name), command:
                generate_button(name, command)
            case int(weight):
                bottom_buttons_frame.columnconfigure(i, weight=weight)
    return bottom_buttons_frame, buttons

@dataclass
class DummyInterface:
    name: str
    frame: ttk.Frame

class DayOfTheWeek(enum.Enum):
    Sunday = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6

def make_calendar(parent: tk.Tk | ttk.Frame, starting_day: DayOfTheWeek, days_in_month: int):
    holder_frame = ttk.Frame(parent, name="calendar", padding=20)
    cal_frame = ttk.Frame(holder_frame, relief=tk.RIDGE, padding=2)
    holder_frame.rowconfigure(1, weight=1)
    holder_frame.columnconfigure(0, weight=1)
    cal_frame.grid(row=1, column=0, sticky="nsew")

    time_selector_frame = ttk.Frame(holder_frame, padding=10)

    left_b, right_b = (
        ttk.Button(time_selector_frame, text=t, width=2)
        for t in "<>"
    )
    month_box = ttk.Combobox(time_selector_frame, justify=tk.CENTER)
    month_box.insert(tk.END, "Decembruary")
    date_box = ttk.Combobox(time_selector_frame)
    date_box.insert(tk.END, "13/6/3322")
    for n in 0, 4:
        time_selector_frame.columnconfigure(n, weight=1, uniform="time_selector_centering")

    for (name, pos) in ("Month", 2), ("Year", 4):
        lbl = ttk.Label(time_selector_frame, text=name)
        lbl.grid(row=0, column=pos, sticky="e")
    
    left_b.grid(row=1, column=1)
    month_box.grid(row=1, column=2)
    right_b.grid(row=1, column=3)
    date_box.grid(row=1, column=4, sticky="e")
    time_selector_frame.grid(row=0, column=0, sticky="ew")

    for i in range(7):
        cal_frame.columnconfigure(i, weight=1, uniform="calendar pane")
    # required_rows = math.ceil((days_in_month + starting_day.value) / 7)
    for j in range(6):
        cal_frame.rowconfigure(j+1, weight=1, uniform="calendar pane")

    def make_frame(column, row):
        frame = ttk.Frame(cal_frame, relief=tk.GROOVE, padding=2)
        frame.grid(row=row, column=column, sticky="news")
        return frame
    day_frames = [[ make_frame(column, row+1) for row in range(6)] for column in range(7)]
    for i, day_of_the_week in enumerate(DayOfTheWeek):
        label = ttk.Label(cal_frame, text=day_of_the_week.name, anchor="center")
        label.grid(row=0, column=i, sticky="ew")
    for day, day_position in enumerate(range(starting_day.value, days_in_month+starting_day.value), start=1):
        column = day_position % 7
        row = day_position // 7
        label = ttk.Label(day_frames[column][row], text=str(day), anchor="nw")
        label.grid()


    bottom_buttons_frame, (edit, add) = make_buttons(holder_frame, ("Edit Meal", 1, "Add Meal"))
    
    bottom_buttons_frame.grid(row=2, column=0, sticky="ew")

    add_event_menu, edit_event_menu = (generate_edit_menu(
        [
            ("Meal", "Foobar Salad", "db search options"),
            ("Time", "10:52", "entry"),
            ("Date", "9/30/26", "entry"),
            ("Repeat", "Until stopping date", "fixed options"),
            ("Interval", "Weekly", "fixed options"),
            ("Stop on", "9/30/27", "entry"),
        ],
        ["Cancel", 1, save_button_name],
    ) for save_button_name in ["Create Event", "Update Event"])

    add.config(command=lambda: em.show_edit_menu(parent.winfo_toplevel(), "Add Event", add_event_menu))
    edit.config(command=lambda: em.show_edit_menu(parent.winfo_toplevel(), "Edit Event", edit_event_menu))
    # TODO: Edit Menu
    return DummyInterface("Calendar", holder_frame)

type EditMenuElem = Literal["entry", "text", "fixed options", "db search options", "list display", "display", "image", "separating bar", "checkbox", "button", "add ingredient"]


placeholder_image: tk.PhotoImage

def generate_edit_menu(options: list[tuple[str, str, EditMenuElem]], bottom_buttons: list[str | int]) -> Callable[[tk.Toplevel], ttk.Frame]:
    def inner(parent: tk.Toplevel) -> ttk.Frame:
        holder = ttk.Frame(parent, padding=10)
        holder.columnconfigure(1, weight=1)
        done_button_row = len(options)+1
        holder.rowconfigure(done_button_row-1, weight=1)

        bottom_buttons_frame, _ = make_buttons(holder, bottom_buttons)
        bottom_buttons_frame.grid(column=0, row=done_button_row, columnspan=2, sticky="ew")

        for i, (name, sample_input, option_type) in enumerate(options):
            holder.rowconfigure(i, pad=4)
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
            if name:
                opt_label = ttk.Label(holder, text=name)
                opt_label.grid(row=i, column=0, sticky="ne")
        return holder
    return inner


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



def make_shopping_list(parent: tk.Tk | ttk.Frame):
    shopping_frame = ttk.Frame(parent, name="shopping", padding=20)

    duration_frame = ttk.Frame(shopping_frame, padding=4)
    duration_label = ttk.Label(duration_frame, text="Covering meals for the next")
    duration_entry = ttk.Combobox(duration_frame)
    duration_entry.insert(tk.END, "7 days")
    duration_label.grid(row=0, column=0)
    duration_entry.grid(row=0, column=1)
    duration_frame.grid(row=0, column=0, columnspan=2)

    list_frame = ttk.Frame(shopping_frame)
    list_frame.columnconfigure(0, weight=1)
    list_frame.rowconfigure(0, weight=1)
    shopping_list = ttk.Treeview(list_frame, columns=["ingr", "qty"], show="headings")
    scrollbar = ttk.Scrollbar(list_frame, command=shopping_list.yview)
    shopping_list.config(yscrollcommand=scrollbar.set)
    shopping_list.heading("ingr", text="Ingredient")
    shopping_list.heading("qty", text="Quantity")
    shopping_list.column("ingr", anchor="w")
    shopping_list.column("qty", anchor="e")
    example_ingredients = [f"Test Ingredient {i}" for i in range(10)]
    test_units = ["lbs", "gal", "oz", "pkgs"]
    for i, ingr in enumerate(example_ingredients, start=1):
        amnt = random.randint(2, 60)
        unit = random.choice(test_units)
        shopping_list.insert("", "end", text="", values=[ingr, f"{amnt} {unit}"])
    scrollbar.grid(row=0, column=1, sticky="ns")
    shopping_list.grid(row=0, column=0, sticky="news")
    list_frame.grid(row=1, column=0, columnspan=2, sticky="news")
    shopping_frame.rowconfigure(1, weight=1)
    shopping_frame.columnconfigure(0, weight=1)
    shopping_frame.columnconfigure(1, weight=1)
    bottom_buttons: list[ttk.Button] = []
    for col, name in enumerate(("Print", "Save to File")):
        button = ttk.Button(shopping_frame, text=name)
        button.grid(row=2, column=col, sticky="ew")
        bottom_buttons.append(button)
    return DummyInterface("Your Shopping List", shopping_frame)

def make_settings(parent: tk.Tk | ttk.Frame):
    
    options_frame = ttk.Frame(parent, name="options", relief = tk.RIDGE, padding=2)

    options = [
            f"Option {i}" for i in range(1, 5)
        ]
    
    options_frame.columnconfigure(0, minsize=40)
    # options_frame.columnconfigure(1, weight=1, uniform="options column")
    options_frame.columnconfigure(2, minsize=4)
    # options_frame.columnconfigure(3, weight=1, uniform="options column")
    options_frame.columnconfigure(4, weight=10)
    options_frame.rowconfigure(0, minsize=40)
    options_frame.rowconfigure(len(options)+1, weight=4)

    mode = 0
    for i, option in enumerate(options, start=1):
        label = ttk.Label(options_frame, anchor="e", text=option)
        button: ttk.Widget
        match mode:
            case 0:
                bvar = tk.IntVar(options_frame, value=0)
                button = ttk.Checkbutton(options_frame, variable=bvar)
                button.config(variable=bvar)
            case 1:
                button = ttk.Entry(options_frame)
                button.insert(0, "Text Input")
            case 2:
                button = ttk.Menubutton(options_frame, text="Options List")
            case _:
                raise Exception("Unreachable")
        mode = (mode + 1) % 3
        label.grid(row=i, column=1, sticky="e")
        button.grid(row=i, column=3, sticky="w")

    return DummyInterface("Settings", options_frame)


if __name__ == '__main__':
    test_ui()


