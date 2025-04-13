from pydantic import BaseModel
from datetime import time
from typing import Optional

'''
Pydantic validation models for the time_slot table endpoints
'''

class TimeSlotCreate(BaseModel):
    schedule_id: Optional[int] = None
    start_time: str
    end_time: str
    is_available: Optional[bool] = True

    class Config:
        arbitrary_types_allowed = True

class TimeSlotUpdate(BaseModel):
    slot_id: int
    schedule_id: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_available: Optional[bool] = None

    class Config:
        arbitrary_types_allowed = True

class TimeSlotChildResponse(BaseModel):
    slot_id: int
    start_time: time
    end_time: time
    is_available: bool
    is_booked: bool

    class Config:
        from_attributes = True

class TimeSlotResponse(TimeSlotCreate):
    slot_id: int
    is_available: bool
    is_booked: bool

    class Config:
        from_attributes = True