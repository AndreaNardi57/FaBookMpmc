from sqlalchemy import Column, Integer, String, Date, Boolean, Float,TIMESTAMP
from database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Categories(Base):
	__tablename__ = "categories"
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable = False)
