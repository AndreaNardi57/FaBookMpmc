from sqlalchemy import Column, Integer, String, Date, Boolean, Float,TIMESTAMP
from database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable = False)
    last_name = Column(String, nullable = False)
    username = Column(String, unique=True, nullable = False)
    password = Column(String)
    email = Column(String, unique=True, nullable = False)
    phone = Column(String)
    is_active = Column(Boolean, default = True)
    status = Column(String)
    created_at = Column(Date, server_default=text(Date_Value))
    
    # loans = relationship("Loan", back_populates="users")
    
