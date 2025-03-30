from pydantic import BaseModel
from typing import Optional
from modules.user.user_schema import UserBase

class BarberCreate(BaseModel):
    user_id: int

class BarberResponse(BaseModel):
    barber_id: int
    user: UserBase

    class Config:
        from_attributes = True