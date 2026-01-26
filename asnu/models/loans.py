from sqlalchemy import Column, Integer, String, Date, Boolean, Float,TIMESTAMP
from database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Loan(Base):
    __tablename__ = "on_loans"

    id = Column(Integer, primary_key=True, index=True)
    copies_id = Column(Integer, ForeignKey("copies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    borrowed = Column(Date, server_default=text(Date_Value))
    due_back = Column(Date, nullable = False)
    return_date = Column(Date)
    notes = Column(Text)
    status = Column(Text)

    # copies = relationship("Copies", back_populates="on_loans")
    # users = relationship("User", back_populates="on_loans")

