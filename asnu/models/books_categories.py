from sqlalchemy import Column, Integer, String, Date, Boolean, Float,TIMESTAMP
from database import Base
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Books_Categories(Base):
	__tablename__ = "books_categories"
	book_id = Column(Integer, ForeignKey("books.id"))
	categories_id = Column(Integer, ForeingKey("categories_id"))

	__table_args__ = (
        Index('books_categories_pkey', 'book_id', 'categories_id'),)

	# book = relationship(Books, foreing_key("Books_Categories.book_id"))
	# category = relationship(Categories, foreing_key("Books_Categories.categories_id"))
