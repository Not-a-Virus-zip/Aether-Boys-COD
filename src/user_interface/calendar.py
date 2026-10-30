from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import calendar
import datetime
import enum
import typing

from . import (
    edit_menu as em,
    user_interface_impl as ui,
    virtual_pantry as vp,
)
from ..backend.meal_catalog import ExistingSimpleMeal
from ..backend.event import SimpleEvent, ExistingSimpleEvent

PANEL_LABEL_NAME = "calendar label"

class Calendar:
    name = "Calendar"

    def __init__(self, parent: ttk.Notebook) -> None:
        self.cal = calendar.Calendar(firstweekday=calendar.SUNDAY)

        self.frame = ttk.Frame(parent, name="calendar", padding=20)
        cal_frame = ttk.Frame(self.frame, relief=tk.RIDGE, padding=2)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        cal_frame.grid(row=1, column=0, sticky="nsew")
        
        time_selector_frame = ttk.Frame(self.frame, relief="groove")

        left_b = ttk.Button(time_selector_frame, text="<", width=2, command=lambda: self.shift_month(-1))
        right_b = ttk.Button(time_selector_frame, text=">", width=2, command=lambda: self.shift_month(1))
        
        self.month_box = ttk.Combobox(time_selector_frame, justify=tk.CENTER, values=list(map(fmt_month_int, calendar.Month)))
        self.month_box.insert(tk.END, "Decembruary")
        self.year_box = ttk.Combobox(time_selector_frame)
        self.year_box.insert(tk.END, "13/6/3322")
        for n in 0, 4:
            time_selector_frame.columnconfigure(n, weight=1, uniform="time_selector_centering")
        
        # for (name, pos) in ("Month", 2), ("Year", 4):
        #     lbl = ttk.Label(time_selector_frame, text=name)
        #     lbl.grid(row=0, column=pos, sticky="e")
        
        left_b.grid(row=1, column=1)
        self.month_box.grid(row=1, column=2)
        right_b.grid(row=1, column=3)
        self.year_box.grid(row=1, column=4, sticky="e")
        time_selector_frame.grid(row=0, column=0, sticky="ew")
        
        for col in range(7):
            cal_frame.columnconfigure(col, weight=1, uniform="calendar pane")
        # required_rows = math.ceil((days_in_month + starting_day.value) / 7)
        for row in range(6):
            cal_frame.rowconfigure(row+1, weight=1, uniform="calendar pane")

        for i, day_of_the_week in enumerate(DayOfTheWeek):
            label = ttk.Label(cal_frame, text=day_of_the_week.name, anchor="center")
            label.grid(row=0, column=i, sticky="ew")
        
        def make_frame(column, row):
            frame = ttk.Frame(cal_frame, relief=tk.GROOVE, padding=2)
            frame.grid(row=row, column=column, sticky="news")
            ttk.Label(frame, name=PANEL_LABEL_NAME, anchor="nw")
            return frame
        
        self.day_frames = [
            make_frame(column, row+1)
            for row in range(6)
            for column in range(7)
        ]

        current_date = datetime.datetime.now()
        self.setup_for_month(current_date.year, current_date.month)

    def shift_month(self, shift: int):
        new_month = ((self.current_month + shift - 1) % 12) + 1
        self.setup_for_month(self.current_year, new_month)

    def setup_for_month(self, year: int, month: int):
        self.current_month = month
        self.current_year = year
        self.month_box.set(fmt_month_int(month))

        for frame, month_n in zip(self.day_frames, self.cal.itermonthdays(year, month)):
            label = frame.children[PANEL_LABEL_NAME]
            assert isinstance(label, ttk.Label)
            if month_n == 0:
                label.grid_remove()
            else:
                label.config(text=str(month_n))
                label.grid()

def fmt_month_int(month_int: calendar.Month | int) -> str:
    return calendar.Month(month_int).name.capitalize()

class DayOfTheWeek(enum.Enum):
    Sunday = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6


class RepeatOptions(enum.Enum):
    UntilStopDate = "Until stopping date"


class EditEvent(em.EditMenuWithSearcher):
    def __init__(self, parent: tk.Misc, event: ExistingSimpleEvent | SimpleEvent) -> None:
        super().__init__(parent)
        self.meal = self.insert_searcher("Meal", em.ClosedDbSearchOptions(self.frame, "Meal", "Missing Meal", self._search_meal, lambda m: m.name))
        self.time = self.insert("Time", em.Entry(self.frame))
        self.date = self.insert("Date", em.DateEntry(self.frame))
    
    def _search_meal(self, query: str) -> list[ExistingSimpleMeal]:
        return []
