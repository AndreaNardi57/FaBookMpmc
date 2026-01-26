from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date


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


