from __future__ import annotations

import itertools as it
import tkinter as tk
from tkinter import ttk

import calendar
import datetime as dt
import enum
from dataclasses import InitVar, dataclass, field
from tkinter import font
from tkinter import messagebox

from . import (
    edit_menu as em,
    user_interface_impl as ui,
)
from ..backend.meal_catalog import ExistingSimpleMeal
from ..backend.event import Event, ExistingEvent

YEAR_SELECT_RANGE = 50
EVENT_NAME_MAX_DISPLAY_LEN_ON_CALENDAR = 50

class Calendar:
    name = "Calendar"

    def __init__(self, parent: ttk.Notebook, backend: ui.Backend) -> None:
        add_calendar_styles(parent)
        self._selected_event: EventDisplay | None = None
        self._selected_panel: CalendarPanel | None = None
        self._selected_date: dt.date | None = None

        self.backend = backend
        self.cal = calendar.Calendar(firstweekday=calendar.SUNDAY)

        self.frame = ttk.Frame(parent, name="calendar", padding=20)
        cal_frame = ttk.Frame(self.frame, relief="groove", padding=2)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
        cal_frame.grid(row=1, column=0, sticky="nsew")
        
        time_selector_frame = ttk.Frame(self.frame, relief="groove", padding=2)

        left_b = ttk.Button(time_selector_frame, text="<", width=2, command=lambda: self.shift_month(-1))
        right_b = ttk.Button(time_selector_frame, text=">", width=2, command=lambda: self.shift_month(1))
        
        self.month_box = ttk.Combobox(time_selector_frame, justify=tk.CENTER, state="readonly", values=list(MONTHS_MAP))
        self.month_box.bind("<<ComboboxSelected>>", self._on_month_selected)

        self.year_box = ttk.Combobox(time_selector_frame, width=10, justify=tk.CENTER, postcommand=self._get_year_options)
        self.year_box.bind("<<ComboboxSelected>>", self._on_year_selected)

        for n in 1, 5:
            time_selector_frame.columnconfigure(n, weight=1, uniform="time_selector_centering")

        # Note, extra padding so the year_box doesn't spill over the bounds
        for n in 0, 6:
            time_selector_frame.columnconfigure(n, minsize=2)
        
        left_b.grid(row=1, column=2)
        self.month_box.grid(row=1, column=3)
        right_b.grid(row=1, column=4)
        self.year_box.grid(row=1, column=5, sticky="e")
        time_selector_frame.grid(row=0, column=0, sticky="ew")
        
        for col in range(7):
            cal_frame.columnconfigure(col, weight=1, uniform="calendar pane")
        for row in range(6):
            cal_frame.rowconfigure(row+1, weight=1, uniform="calendar pane")

        for i, day_of_the_week in enumerate(DayOfTheWeek):
            label = ttk.Label(cal_frame, text=day_of_the_week.name, anchor="center")
            label.grid(row=0, column=i, sticky="ew")
        
        def make_frame(column, row):
            frame = ttk.Frame(cal_frame, name=f"calendar_panel_{column}x{row}", relief=tk.GROOVE, padding=2, style="CalendarPanel.TFrame")

            # Fixes a visual bug where the panels shift slightly whenever the text on buttons updates 
            frame.grid_propagate(False)

            frame.columnconfigure(1, weight=1)
            frame.rowconfigure(1, weight=1)
            frame.grid(row=row, column=column, sticky="news")
            num_lbl = ttk.Label(frame, anchor="nw", style="CalendarDayLabel.TLabel")
            num_lbl.grid(row=0, column=0)
            event_panel = ttk.Frame(frame, padding=2, style="CalendarEventFrame.TFrame")
            event_panel.grid(row=1, column=0, columnspan=2, sticky="nsew")
            event_panel.columnconfigure(0, weight=1)
            return CalendarPanel(self, frame, num_lbl, event_panel, [], 0)
        
        self.day_frames = [
            make_frame(column, row+1)
            for row in range(6)
            for column in range(7)
        ]

        # dummy value to simplify code
        self.current_today_panel = self.day_frames[0]

        button_frame, (
            self.delete_button,
            self.add_button,
            self.edit_button,
        ) = ui.make_buttons(
            self.frame, (
                ("Delete Selected", self.press_delete_button),
                ("Add New", self.press_add_button),
                ("Edit Selected", self.press_edit_button),
            ),
            button_weight=1
        )
        for b in self.edit_button, self.delete_button:
            b.state(("disabled",))

        button_frame.grid(row=2, column=0, sticky="nsew")

        now = dt.datetime.now()
        self.switch_calendar_to(now.date().replace(day=1))

    def press_delete_button(self):
        event = self._selected_event
        if event is None:
            return
        if messagebox.askokcancel(
            "Confirm Deletion",
            f"Are you sure you want to delete \"{event.event.meal_name}\" from your calendar?",
            icon=messagebox.WARNING,
            default=messagebox.CANCEL,
            parent=self.frame,
        ):
            self.backend.event.delete_event(event.event)
            self.refresh_calendar()

    def press_add_button(self):
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Edit Event",
            lambda tl: EditEvent(tl, self, self.backend).frame,
        )

    def press_edit_button(self):
        event_disp = self._selected_event
        if event_disp is None or not event_disp.alive:
            return
        event = event_disp.event
        em.show_edit_menu(
            self.frame.winfo_toplevel(),
            "Edit Event",
            lambda tl: EditEvent(tl, self, self.backend, event).frame,
        )

    def set_selected_event(self, new_selection: EventDisplay | None):
        if self._selected_event is not None and new_selection is not self._selected_event and self._selected_event.alive:
            self._selected_event.set_selected(False)
        self._selected_event = new_selection
        new_state = ("disabled" if new_selection is None else "!disabled",)
        self.edit_button.state(new_state)
        self.delete_button.state(new_state)

    def set_selected_panel(self, new_selection: CalendarPanel | None):
        if self._selected_panel is not None:
            self._selected_panel.set_state(selected=False)
        if new_selection is None:
            self._selected_panel = None
            self._selected_date = None
        else:
            new_selection.set_state(selected=True)
            self._selected_panel = new_selection
            self._selected_date = self.visible_date.replace(day=new_selection.current_day)

    def is_panel_selected(self, panel: CalendarPanel) -> bool:
        return panel is self._selected_panel

    def get_date_for_new_event(self):
        return self.visible_date if self._selected_date is None else self._selected_date

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

    def refresh_calendar(self):
        self.switch_calendar_to(self.visible_date)

    def switch_calendar_to(self, new_date: dt.date):
        """Sets the calendar to the month containing the given date"""
        self.set_selected_event(None)

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
            panel.current_day = day_n
            if day_n == 0:
                panel.frame.state(("disabled",))
                panel.number_label.grid_remove()
                panel.event_frame.grid_remove()
            else:
                panel.frame.state(("!disabled",))
                days.append(panel)
                panel.number_label.config(text=str(day_n))
                panel.number_label.grid()
                panel.event_frame.grid()
                for ev in panel.events:
                    ev.destroy()
                panel.events.clear()
        
        events = self.backend.event.get_simple_event(*month_span(self.visible_date))
        for event in events:
            try:
                tgt_panel = days[event.scheduled_at.day-1]
            except IndexError as e:
                # bad db info?
                print(f"IndexError: {e}") # TODO: Logging
                continue
            event_disp = EventDisplay(event, self.backend, self, tgt_panel.event_frame)
            event_disp.button.grid(row=len(tgt_panel.events), column=0, sticky="ew")
            tgt_panel.events.append(event_disp)
        
        self.current_today_panel.set_state(today=False)
        today = dt.date.today()
        if today.year == year and today.month == month:
            self.current_today_panel = days[today.day-1]
            self.current_today_panel.set_state(today=True)

@dataclass
class CalendarPanel:
    cal: Calendar
    frame: ttk.Frame
    number_label: ttk.Label
    event_frame: ttk.Frame
    events: list[EventDisplay]
    current_day: int

    def __post_init__(self):
        for w in self.frame, self.number_label, self.event_frame:
            w.bind("<Button-1>", self._on_click)
            w.bind("<Double-Button-1>", self._on_double_click)

    def _on_click(self, event: tk.Event):
        if self.frame.instate(("!disabled",)):
            self.cal.set_selected_panel(
                None
                if self.cal.is_panel_selected(self) else
                self
            )

    def _on_double_click(self, event: tk.Event):
        if self.frame.instate(("!disabled",)):
            self.cal.set_selected_panel(self)
            self.cal.press_add_button()

    def set_state(self, **kwargs: bool):
        statespec = tuple(it.starmap(custom_state, kwargs.items()))
        self.frame.state(statespec)
        self.number_label.state(statespec)
        self.event_frame.state(statespec)
        for event in self.events:
            event.button.state(statespec)

@dataclass
class EventDisplay:
    event: ExistingEvent
    backend: ui.Backend
    cal: Calendar

    button: ttk.Button = field(init=False)
    alive: bool = field(init=False, default=True)

    _full_text: str = field(init=False)
    _display_text: str = field(init=False)
    _font: font.Font = field(init=False)
    _selected: bool = field(init=False, default=False)
    _previous_width: int = field(init=False, default=-1)

    parent: InitVar[tk.Misc]

    def __post_init__(self, parent: tk.Misc):
        self.button = ttk.Button(parent, text=self.event.meal_name, width=0, style="EventDisplay.TButton", command=self._on_click)
        self._full_text = self.button["text"]
        self._display_text = self._full_text[:EVENT_NAME_MAX_DISPLAY_LEN_ON_CALENDAR]
        self._font = font.Font(font=ttk.Style().lookup(self.button["style"], "font"))
        self.button.bind("<Configure>", self._on_resize)
        self.button.bind("<Double-Button-1>", self._on_double_click)

    def _on_resize(self, event: tk.Event):
        new_width = event.width
        if new_width == self._previous_width:
            return
        self._previous_width = new_width
        available_width = max(new_width - 8, 0)
        truncated_text = truncate_text_to_fit_button(self._font, self._display_text, available_width)
        self.button.config(text=truncated_text)

    def _on_double_click(self, event: tk.Event):
        prev_state = self._selected
        self.set_selected(True)
        self.cal.press_edit_button()
        self.set_selected(prev_state)

    def set_selected(self, new_state: bool):
        if new_state != self._selected:
            self._selected = new_state
            self.button.state(("pressed" if new_state else "!pressed",))
            self.cal.set_selected_event(self if new_state else None)
    
    def _on_click(self):
        self.set_selected(not self._selected)

    def destroy(self):
        self.alive = False
        self.button.destroy()

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

def truncate_text_to_fit_button(font: font.Font, base_text: str, available_width: int) -> str:
    if available_width < 1 or available_width < font.measure(base_text[0]):
        return ""

    total_width_required = font.measure(base_text)
    
    if total_width_required <= available_width:
        return base_text

    # make room for the dash
    available_width -= font.measure("-")

    curr = 0
    for i, c in enumerate(base_text):
        curr += font.measure(c)
        if curr > available_width:
            return base_text[:i-1] + "-"
    return base_text

# used for styling
custom_state_dictionary = {
    "today": "user1" # state when a calendar frame is today's date
}

def custom_state(st: str, active: bool = True):
    if active:
        return custom_state_dictionary.get(st, st)
    else:
        return f"!{custom_state_dictionary.get(st, st)}"

def add_calendar_styles(parent: tk.Misc):
    style = ttk.Style(parent)
    selected = ("selected", "light blue")
    today = (custom_state("today"), "light green")
    selected_and_today = (custom_state("today"), "selected", "cyan")
    panel_modes = selected_and_today, selected, today
    style.map("CalendarPanel.TFrame",
        background=[("disabled", "light gray"), *panel_modes],
    )
    style.map("CalendarEventFrame.TFrame",
        background=[*panel_modes],
    )
    style.map("CalendarDayLabel.TLabel",
        background=[*panel_modes],
    )
    
    style.configure("EventDisplay.TButton",
        anchor="w",
    )
    style.map("EventDisplay.TButton",
        background=[*panel_modes],
    )


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
    def __init__(self, container: tk.Misc, cal: Calendar, backend: ui.Backend, event: ExistingEvent | None = None) -> None:
        super().__init__(container)
        if event is not None:
            initial_meal = backend.meals.get_simple_meal(event.meal_id) if event is not None else None
            starting_date = event.scheduled_at.date() if event is not None else cal.visible_date
            starting_time = event.scheduled_at.timetz().isoformat()
        else:
            initial_meal = None
            starting_date = cal.get_date_for_new_event()
            starting_time = dt.time(12,0).isoformat()

        self.backend = backend
        self.calendar = cal
        self.container = container
        self.event = event
        self.date = self.insert("Date", em.DateEntry(self.frame, starting_date))
        self.time = self.insert("Time", em.CheckedEntry(self.frame, em.CheckForException("Unknown Time", dt.time.fromisoformat), starting_time))
        self.meal = self.insert_searcher(
            "Meal",
            em.ClosedDbSearchOptions(
                self.frame,
                "Meal",
                "Missing Meal",
                self._search_meal,
                lambda m: m.name,
                initial_value=initial_meal,
                selection_callback=self._on_selected_meal_change)
        )
        self.meal_description = self.insert("Description", em.WrappingDisplay(self.frame, "", width=40))
        self.meal_recipe = self.insert("Recipe", em.WrappingDisplay(self.frame, "", width=40))
        self._on_selected_meal_change(initial_meal)

        self.cancel_button, self.save_button = self.finish_construction([("Cancel", container.destroy), 1, ("Save Changes", self.save_and_close)])

    def _on_selected_meal_change(self, selected_meal: ExistingSimpleMeal | None):
        if selected_meal is None:
            self.meal_description.elem.set_text("N/A")
            self.meal_recipe.elem.set_text("N/A")
        else:
            self.meal_description.elem.set_text(selected_meal.description.strip() or "N/A")
            detailed_meal = self.backend.meals.get_detailed_meal(selected_meal.id)
            self.meal_recipe.elem.set_text(detailed_meal.recipe.strip() or "N/A")

    def _search_meal(self, query: str) -> list[ExistingSimpleMeal]:
        return self.backend.meals.get_simple_meals(search_term=query)

    def save_and_close(self):
        if not self.check_all_input_and_show_errors():
            # TODO: Pop-up error?
            return
        new_meal = self.meal.elem.get_selection()
        assert new_meal is not None
        new_time = dt.time.fromisoformat(self.time.elem.get_text())
        new_date = self.date.elem.get_date()
        new_dt = dt.datetime.combine(new_date, new_time)
        match self.event:
            case ExistingEvent() as e:
                self.backend.event.update_event(e.modify(meal_id=new_meal.id, meal_name=new_meal.name, scheduled_at=new_dt))
            case None:
                self.backend.event.create_event(Event(new_meal.id, new_dt))

        self.calendar.refresh_calendar()
        self.container.destroy()
    
