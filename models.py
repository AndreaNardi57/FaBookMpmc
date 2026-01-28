from sqlalchemy import Column, Integer, String, Date, Boolean, Float, TIMESTAMP, Text
from database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

# Date_Value = 'curdate()'
Date_Value = 'CURRENT_DATE'


class Book(Base):
	__tablename__ = "books"
	id = Column(Integer, primary_key=True, index = True)
	title = Column(Text, nullable = False)
	author = Column(Text, nullable = False)
	isbn = Column(String)
	publisher = Column(Text)
	yearpubblish = Column(Integer)
	release = Column(Text)
	language = Column(String)
	description = Column(Text)
	created_at = Column(Date, server_default=text(Date_Value))

	# loans = relationship("Loan", back_populates="books")

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

class Copies(Base):
	__tablename__ = "copies"
	id = Column(Integer, primary_key=True, index=True)
	book_id = Column(Integer, nullable = False)
	lay = Column(String)
	status = Column(Text)
	conditions = Column(String)
	notes = Column(Text)

	# books = relationship(Books, back_populates("copies"))

class Loan(Base):
    __tablename__ = "on_loan"

    id = Column(Integer, primary_key=True, index=True)
    copies_id = Column(Integer, nullable = False)
    user_id = Column(Integer, nullable = False)
    borrowed = Column(Date, server_default=text(Date_Value))
    due_back = Column(Date, nullable = False)
    return_date = Column(Date)
    notes = Column(Text)
    status = Column(Text)

    # copies = relationship("Copies", back_populates="on_loans")
    # users = relationship("User", back_populates="on_loans")
