from pydantic import BaseModel
from datetime import time
from typing import Optional

'''
Pydantic validation models for the schedule table endpoints
'''

class ScheduleCreate(BaseModel):
    barber_id: int
    appointment_id: Optional[int] = None #schedule blocks initially are not associated with an appointment
    date: str
    startTime: time
    endTime: time

    class Config:
        arbitrary_types_allowed = True

class ScheduleUpdate(BaseModel):
    barber_id: Optional[int] = None
    appointment_id: Optional[int] = None #schedule blocks initially are not associated with an appointment
    date: Optional[str] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None

    class Config:
        arbitrary_types_allowed = True

class ScheduleResponse(ScheduleCreate):
    schedule_id: int

    class Config:
        from_attributes = True