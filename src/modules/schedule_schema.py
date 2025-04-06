from pydantic import BaseModel
from typing import Optional
from .time_slot_schema import TimeSlotChildResponse, TimeSlotCreate, TimeSlotUpdate
from .user.barber_schema import BarberResponse
import datetime

'''
Pydantic validation models for the schedule table endpoints
'''

class ScheduleCreate(BaseModel):
    barber_id: int
    date: datetime.date
    is_working: Optional[bool] = True
    time_slots: list[TimeSlotCreate]

    class Config:
        arbitrary_types_allowed = True

class ScheduleUpdate(BaseModel):
    barber_id: Optional[int] = None
    date: Optional[datetime.date] = None
    is_working: Optional[bool] = None
    time_slots: Optional[list[TimeSlotUpdate]] = None

    class Config:
        arbitrary_types_allowed = True

class ScheduleResponse(ScheduleCreate):
    schedule_id: int
    is_working: bool
    time_slots: list[TimeSlotChildResponse]
    barber: BarberResponse

    class Config:
        from_attributes = True