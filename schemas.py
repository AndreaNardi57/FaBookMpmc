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
    return_date: date
    notes: str
    status: str
        
class LoanCreate(LoanBase):
    pass

class Loan(LoanBase):
    id: int

    class Config:
        from_attributes = True
