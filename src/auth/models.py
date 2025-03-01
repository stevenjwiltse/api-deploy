from pydantic import BaseModel
from typing import Optional, List, Dict

class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    roles: List


