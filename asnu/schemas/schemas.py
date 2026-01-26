from pydantic import BaseModel, Field
from pydantic_extra_types.pendulum_dt import Date
from typing import Optional
from datetime import date

class BookBase(BaseModel):
    operazione: str
    dataRitiro: str
    dataChiusura: str
    autore: str
    titolo: str
    
class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int

    class Config:
        orm_mode = True
