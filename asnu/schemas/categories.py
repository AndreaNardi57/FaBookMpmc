from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date


class CategoryBase(BaseModel):
    name: str
    
class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True


