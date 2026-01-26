from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date


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


