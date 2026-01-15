from sqlalchemy.orm import Session
from models import Book
from schemas import BookCreate
import schemas
import crud
from datetime import datetime
from sqlalchemy import or_

def get_book_by_search(db: Session, query: str,search_field: str,skip: int = 0,limit: int = 1000):
    if search_field == "title":
        return db.query(Book).filter(Book.title.ilike(f"%{query}%")).order_by(Book.author.desc()).offset(skip).limit(limit).all()
    elif search_field == "author":
        return db.query(Book).filter(Book.author.ilike(f"%{query}%")).order_by(Book.author.desc()).offset(skip).limit(limit).all()

def get_books_count_filtered(db: Session, query: str):
    return db.query(Book).filter(or_(Book.title.ilike(f"%{query}%"),Book.author.ilike(f"%{query}%"))).count()

def get_books(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(Book).order_by(Book.author.desc()).offset((skip-1)*limit).limit(limit).all()

def get_books_count(db: Session):
    return db.query(Book).count()

def create_book(db: Session, book: BookCreate):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, id: str, book_update: BookCreate):
    db_book = db.query(Book).filter(Book.id == id).first()
    if db_book:
        for key, value in book_update.dict().items():
            setattr(db_book, key, value)
        db.commit()
        db.refresh(db_book)
    return db_book

def delete_book(db: Session, id: str):
    db_book = db.query(Book).filter(Book.id == id).first()
    if db_book:
        db.delete(db_book)
        db.commit()
    return db_book

