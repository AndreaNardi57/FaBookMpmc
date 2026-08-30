from sqlalchemy import Column, Integer, String, Date, Boolean, Float, TIMESTAMP, Text, ForeignKey, DateTime
from database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship, backref
from datetime import datetime

# Date_Value = 'curdate()'
Date_Value = 'CURRENT_DATE'


class Book(Base):
    __tablename__ = "books"
    __table_args__ = {"schema": "pescatorello"}

    id = Column(Integer, primary_key=True, index = True)
    title = Column(Text, nullable = False)
    author = Column(Text, nullable = False)
    isbn = Column(String)
    publisher = Column(Text)
    yearpubblish = Column(Integer, nullable = True)
    release = Column(Text)
    language = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    copies = relationship("Copies", back_populates="book")

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "pescatorello"}
	    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable = False)
    email = Column(String, unique=True, nullable = False)
    first_name = Column(String, nullable = False)
    last_name = Column(String, nullable = False)
    phone = Column(String, nullable = True)
    hashed_password = Column(String)
    role = Column(String, nullable=False, default="user")   # admin | librarian | user
    is_active = Column(Boolean, default = True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
	    
    ## loans = relationship("Loan", back_populates="users")

class Copies(Base):
    __tablename__ = "copies"
    __table_args__ = {"schema": "pescatorello"}

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('pescatorello.books.id'), nullable = False)
    lay = Column(String)
    status = Column(Text)
    conditions = Column(String)
    notes = Column(Text)

    book = relationship("Book", back_populates="copies")
    loans = relationship("Loan", back_populates="copy")

class Loan(Base):
    __tablename__ = "on_loan"
    __table_args__ = {"schema": "pescatorello"}

    id = Column(Integer, primary_key=True, index=True)
    copies_id = Column(Integer, ForeignKey('pescatorello.copies.id'), nullable = False)
    user_id = Column(Integer, ForeignKey('pescatorello.users.id'), nullable = False)
    borrowed = Column(Date, server_default=text(Date_Value))
    due_back = Column(Date, nullable = False)
    return_date = Column(Date)
    notes = Column(Text)
    status = Column(Text)

    copy = relationship("Copies", back_populates="loans")
    ## users = relationship("User", back_populates="on_loans")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "pescatorello"}

    id = Column(Integer, primary_key=True)
    actor_id = Column(Integer, ForeignKey("pescatorello.users.id"), nullable=False)
    action = Column(String, nullable=False)
    target = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
