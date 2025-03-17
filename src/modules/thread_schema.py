from pydantic import BaseModel
from typing import List, Optional
from modules.message_schema import MessageResponse

class ThreadBase(BaseModel):
    receivingUser: int
    sendingUser: int

class ThreadCreate(ThreadBase):
    pass

class ThreadResponse(ThreadBase):
    thread_id: int
    messages: Optional[List["MessageResponse"]] = []

    class Config:
        from_attributes = True