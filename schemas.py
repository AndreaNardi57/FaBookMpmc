from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date


class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    publisher: str
    yearpubblish: str
    release: str
    language: str
    description: str
    created_at: date
    
class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    hashed_password: str
    role: str
    is_active: bool
    created_at: date

    @field_validator("phone", mode="before")
    def empty_string_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v

            
class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class CopiesBase(BaseModel):
    book_id: int
    lay: str
    status: str
    condition: str
    notes: str
    
class CopiesCreate(CopiesBase):
    pass

class Copies(CopiesBase):
    id: int

    class Config:
        from_attributes = True

class LoanBase(BaseModel):
    copies_id: int
    user_id: int
    borrowed: date
    due_back: date
    return_date: date | None = None
    notes: str | None = None
    status: str
        
class LoanCreate(LoanBase):
    pass

class Loan(LoanBase):
    id: int

    class Config:
        from_attributes = True

class AuditBase(BaseModel):
    actor_id: int
    action: str
    target: str
    timestamp: date

class AuditCreate(AuditBase):
    pass

class Audit(AuditBase):
    id: int

    class Config:
        from_attributes = True