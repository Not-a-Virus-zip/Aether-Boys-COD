from __future__ import annotations
from dataclasses import dataclass
import dataclasses

import pint

from . import (
    ingredient_list as il,
    existing,
    units,
    backend_tools as bt,
)

from ..database import (
    database_logic as db,
    database_tools as dt,
)

from datetime import (
    datetime,
    date,
    time,
    timedelta,
)

@dataclass(frozen=True)
class SimpleEvent:
    meal_id: int
    meal_name: str
    scheduled_at: datetime

    modify = dataclasses.replace

    __post_init__ = existing.type_check_self

@dataclass(frozen=True)
class ExistingSimpleEvent(SimpleEvent):
    event_id: int

    modify = existing.modify


class EventManager():
    def get_simple_event(self,
                         start_date: date,
                         end_date: date
                         )-> list[ExistingSimpleEvent]:
        return [
            ExistingSimpleEvent(meal_id, meal_name, 
                        datetime.combine(date.fromisoformat(date_str), time.fromisoformat(time_str)), event_id)
            for event_id, date_str, time_str, meal_id, meal_name in db.SimpleEventQuery.run_select()
        ]