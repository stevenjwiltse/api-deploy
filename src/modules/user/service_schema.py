from datetime import time
from decimal import Decimal
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Float


class ServiceBase(BaseModel):
    name: str
    duration: int
    price: Annotated[Decimal, Field(ge=0, max_digits=5, decimal_places=2)]
    category: str
    description: str
    popularity_score: int

class ServiceResponse(ServiceBase):
    service_id: int

    class Config:
        from_attributes = True

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    duration: Optional[int] = None
    price: Annotated[Decimal, Field(ge=0, max_digits=5, decimal_places=2)] = None
    category: Optional[str] = None
    description: Optional[str] = None
    popularity_score: Optional[str] = None
