from sqlalchemy import Column, Integer, String, Date, Boolean, Float,TIMESTAMP
from database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Copies(Base):
	__tablename__ = "copies"
	id = Column(Integer, primary_key=True, index=True)
	book_id = Column(Integer, ForeignKey("books.id"))
	lay = Column(String)
	status = Column(Text)
	conditions = Column(String)
	notes = Column(Text)

	# books = relationship(Books, back_populates("copies"))