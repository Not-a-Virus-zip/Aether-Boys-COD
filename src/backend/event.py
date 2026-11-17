from __future__ import annotations

from dataclasses import dataclass
import dataclasses
from datetime import (
    datetime,
    date,
    time,
    timedelta,
)

from . import (
    ingredient_list as il,
    meal_catalog as mc,
    existing,
    units,
    backend_tools as bt,
)

from ..database import (
    database_logic as db,
    database_tools as dt,
)
from ..user_interface import user_interface_impl as ui
from ..update_flags import DataUpdate


@dataclass(frozen=True)
class Event:
    meal_id: int
    scheduled_at: datetime

    modify = dataclasses.replace

    __post_init__ = existing.type_check_self

@dataclass(frozen=True)
class ExistingEvent(Event):
    event_id: int
    meal_name: str

    modify = existing.modify


class EventManager:
    def __init__(self, app: ui.Application) -> None:
        self.app = app

    def broadcast_changes_to_ui(self):
        self.app.handle_update(DataUpdate.Calendar)
    
    def get_simple_event(self,
                         start_date: date,
                         end_date: date
                         )-> list[ExistingEvent]:
        """Insert needed dates as 'YYYY-MM-DD' (inclusive, inclusive)"""
        return [
            ExistingEvent(meal_id, 
                        datetime.combine(date.fromisoformat(date_str), time.fromisoformat(time_str)), event_id, meal_name)
            for event_id, date_str, time_str, meal_id, meal_name 
            in db.EventQuery.run_select(filter_column='date', filter_value=(date.isoformat(start_date), date.isoformat(end_date)), between=True)
        ]

    def create_event(self, event: Event)-> None:
        db.EventQuery.run_insert(event.scheduled_at.date().isoformat(), 
                                 event.scheduled_at.time().isoformat(timespec='minutes'), event.meal_id)
        self.broadcast_changes_to_ui()

    def delete_event(self, event: ExistingEvent)-> None:
        db.EventQuery.run_delete(event.event_id)
        self.broadcast_changes_to_ui()

    def update_event(self, event: ExistingEvent)-> None:
        db.EventQuery.run_update(event.event_id, event.scheduled_at.date().isoformat(), 
                                 event.scheduled_at.time().isoformat(timespec='minutes'), event.meal_id)
        self.broadcast_changes_to_ui()
