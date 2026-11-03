from __future__ import annotations

import itertools as it
import tkinter as tk
from tkinter import ttk

import calendar
import datetime as dt
import enum
from dataclasses import dataclass

from . import (
    edit_menu as em,
    user_interface_impl as ui,
)
from ..backend.meal_catalog import ExistingSimpleMeal
from ..backend.event import Event, ExistingEvent

YEAR_SELECT_RANGE = 50

class Calendar:
    name = "Calendar"

    def __init__(self, parent: ttk.Notebook, backend: ui.Backend) -> None:
        style = ttk.Style(parent)
        style.map("CalendarFrame.TFrame",
            # Note: our typechecker gives style.map the wrong return type
            background=[("disabled", "light gray"), *style.map("CalendarFrame.TFrame", "background")], # pyright: ignore[reportArgumentType]
        )

        self.backend = backend
        self.cal = calendar.Calendar(firstweekday=calendar.SUNDAY)

        self.frame = ttk.Frame(parent, name="calendar", padding=20)
        cal_frame = ttk.Frame(self.frame, relief=tk.RIDGE, padding=2)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        cal_frame.grid(row=1, column=0, sticky="nsew")
        
        time_selector_frame = ttk.Frame(self.frame, relief="groove")

        left_b = ttk.Button(time_selector_frame, text="<", width=2, command=lambda: self.shift_month(-1))
        right_b = ttk.Button(time_selector_frame, text=">", width=2, command=lambda: self.shift_month(1))
        
        self.month_box = ttk.Combobox(time_selector_frame, justify=tk.CENTER, state="readonly", values=list(MONTHS_MAP))
        self.month_box.bind("<<ComboboxSelected>>", self._on_month_selected)

        self.year_box = ttk.Combobox(time_selector_frame, width=10, justify=tk.CENTER, postcommand=self._get_year_options)
        self.year_box.bind("<<ComboboxSelected>>", self._on_year_selected)

        for n in 0, 4:
            time_selector_frame.columnconfigure(n, weight=1, uniform="time_selector_centering")
        
        left_b.grid(row=1, column=1)
        self.month_box.grid(row=1, column=2)
        right_b.grid(row=1, column=3)
        self.year_box.grid(row=1, column=4, sticky="e")
        time_selector_frame.grid(row=0, column=0, sticky="ew")
        
        for col in range(7):
            cal_frame.columnconfigure(col, weight=1, uniform="calendar pane")
        for row in range(6):
            cal_frame.rowconfigure(row+1, weight=1, uniform="calendar pane")

        for i, day_of_the_week in enumerate(DayOfTheWeek):
            label = ttk.Label(cal_frame, text=day_of_the_week.name, anchor="center")
            label.grid(row=0, column=i, sticky="ew")
        
        def make_frame(column, row):
            frame = ttk.Frame(cal_frame, relief=tk.GROOVE, padding=2, style="CalendarFrame.TFrame")
            frame.columnconfigure(1, weight=1)
            frame.rowconfigure(1, weight=1)
            frame.grid(row=row, column=column, sticky="news")
            num_lbl = ttk.Label(frame, anchor="nw")
            num_lbl.grid(row=0, column=0)
            event_panel = ttk.Frame(frame, padding=2)
            event_panel.grid(row=1, column=0, columnspan=2, sticky="nsew")
            event_panel.columnconfigure(0, weight=1)
            return CalendarPanel(frame, num_lbl, event_panel, [])
        
        self.day_frames = [
            make_frame(column, row+1)
            for row in range(6)
            for column in range(7)
        ]

        now = dt.datetime.now()
        self.switch_calendar_to(now.date().replace(day=1))

    def _on_year_selected(self, event: tk.Event):
        selection = self.month_box.get()
        try:
            selection = int(selection)
        except ValueError:
            return
        self.switch_calendar_to(self.visible_date.replace(year=selection))

    def _on_month_selected(self, event: tk.Event):
        selection = self.month_box.current()
        if selection == -1:
            return
        self.switch_calendar_to(self.visible_date.replace(month=selection+1))

    def shift_month(self, shift: int):
        self.switch_calendar_to(add_months(self.visible_date, shift))

    def _get_year_options(self):
        year = self.visible_date.year
        return list(map(str, range(year - 50, year + 50)))

    def update_year_box(self):
        new_year = self.visible_date.year
        self.year_box.config(values=list(map(str, range(new_year - YEAR_SELECT_RANGE, new_year + YEAR_SELECT_RANGE))))
        self.year_box.current(YEAR_SELECT_RANGE)

    def switch_calendar_to(self, new_date: dt.date):
        """Sets the calendar to the month containing the given date"""
        self.visible_date = new_date

        year = self.visible_date.year
        month = self.visible_date.month
        # set month dropdown to correct month
        if self.month_box.current() != month - 1:
            self.month_box.current(month - 1)

        self.update_year_box()
        self.year_box.set(self.visible_date.year)

        days: list[CalendarPanel] = []
        # update labels on day boxes in calendar
        for panel, day_n in zip(
            self.day_frames,
            # after we finish with the days in the current month, we still need to clear the remaining frames
            it.chain(self.cal.itermonthdays(year, month), it.repeat(0))
        ):
            if day_n == 0:
                panel.frame.state(("disabled",))
                panel.number_label.grid_remove()
                panel.event_display.grid_remove()
            else:
                panel.frame.state(("!disabled",))
                days.append(panel)
                panel.number_label.config(text=str(day_n))
                panel.number_label.grid()
                panel.event_display.grid()
                for ev in panel.events:
                    ev.destroy()
                panel.events.clear()
        
        events = self.backend.event.get_simple_event(*month_span(self.visible_date))
        for event in events:
            try:
                tgt_panel = days[event.scheduled_at.day]
            except IndexError as e:
                # bad db info?
                print(f"IndexError: {e}") # TODO: Logging
                continue
            event_lbl = ttk.Label(tgt_panel.event_display, text=event.meal_name)
            event_lbl.grid(row=len(tgt_panel.events), column=0, sticky="ew")
            tgt_panel.events.append(event_lbl)
            


@dataclass
class CalendarPanel:
    frame: ttk.Frame
    number_label: ttk.Label
    event_display: ttk.Frame
    events: list[EventDisplay]

type EventDisplay = ttk.Label

AVG_MONTH_LEN = 365.25 / 12

def add_months(date: dt.date, shift: int):
    return (
        date.replace(day=15) + dt.timedelta(days=AVG_MONTH_LEN * shift)
    ).replace(day=1)

def month_span(date: dt.date) -> tuple[dt.date, dt.date]:
    """returns the first and last day of given date's month"""
    _, days_in_month = calendar.monthrange(date.year, date.month)
    start = date.replace(day=1)
    end = start.replace(day=days_in_month)
    return start, end

def fmt_month_int(month_int: calendar.Month | int) -> str:
    return calendar.Month(month_int).name.capitalize()

MONTHS_MAP = {fmt_month_int(month): month for month in calendar.Month}

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
    def __init__(self, parent: tk.Misc, backend: ui.Backend, event: ExistingEvent | Event) -> None:
        super().__init__(parent)
        initial_meal = backend.meals.get_simple_meal(event.meal_id)

        self.backend = backend
        self.meal = self.insert_searcher(
            "Meal",
            em.ClosedDbSearchOptions(self.frame, "Meal", "Missing Meal", self._search_meal, lambda m: m.name, initial_value=initial_meal)
        )
        self.time = self.insert("Time", em.Entry(self.frame))
        self.date = self.insert("Date", em.DateEntry(self.frame))
    
    def _search_meal(self, query: str) -> list[ExistingSimpleMeal]:
        return self.backend.meals.get_simple_meals(search_term=query)
