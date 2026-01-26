from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date


class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    email: str
    phone: str
    is_active: bool
    status: str
    created_at: date
    
class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True


