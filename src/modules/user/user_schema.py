from pydantic import BaseModel, EmailStr

'''
Pydantic validation models for the users table endpoints
'''

class UserBase(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    phoneNumber: str
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int

    class Config:
        from_attributes = True
