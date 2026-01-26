from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date


class BookCatBase(BaseModel):
    book_id: int
    categories_id: int
    
class BookCatCreate(BookCatBase):
    pass

class BookCat(BookCatBase):
    class Config:
        from_attributes = True


