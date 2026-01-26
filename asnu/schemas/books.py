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

