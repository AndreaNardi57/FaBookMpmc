# Source - https://stackoverflow.com/a
# Posted by vaultah, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-12, License - CC BY-SA 3.0

from pathlib import Path
print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

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
