from pydantic import BaseModel
from typing import Optional
from enum import Enum

from modules.user.user_schema import UserResponse
from modules.user.barber_schema import BarberResponse
from modules.user.service_schema import ServiceResponse
from modules.time_slot_schema import TimeSlotChildResponse


'''
Pydantic validation models for the appointment table endpoints
'''

class AppointmentStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"

class AppointmentCreate(BaseModel):
    user_id: int
    barber_id: int
    status: AppointmentStatus 
    time_slot: list[int]
    service_id: list[int]

class AppointmentUpdate(BaseModel):
    user_id: Optional[int] = None
    barber_id: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    time_slot: Optional[list[int]] = None
    service_id: Optional[list[int]] = None

class AppointmentResponse(BaseModel):
    appointment_id: int
    user: UserResponse
    barber: BarberResponse
    status: AppointmentStatus
    time_slots: list[TimeSlotChildResponse] 
    services: list[ServiceResponse]


    class Config:
        from_attributes = True