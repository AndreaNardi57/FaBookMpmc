from sqlalchemy.orm import Session
from sqlalchemy import select, desc
## from models import Book
## from schemas import BookCreate
import models
import schemas
import crud
from models import Book, Copies, User, Loan
from schemas import BookCreate

from datetime import datetime, timedelta
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

def get_loans(db: Session):
    stmt = (
        db.query(
            Book.title,
            Book.author,
            Loan.status,
            Copies.id,
            User.username,
            Loan.borrowed,
            Loan.due_back,
            Loan.return_date
            )
        .join(Copies, Copies.book_id == Book.id)
        .join(Loan, Loan.copies_id == Copies.id)
        .join(User, User.id == Loan.user_id)
    ).order_by(Loan.borrowed)

    results = stmt.all()
    return results

def get_loans_lst(db: Session):
    stmt = (
        db.query(
            Book.title,
            Book.author,
            Loan.status,
            Copies.id,
            User.username,
            Loan.borrowed,
            Loan.due_back,
            Loan.return_date
            )
        .join(Copies, Copies.book_id == Book.id)
        .join(Loan, Loan.copies_id == Copies.id)
        .join(User, User.id == Loan.user_id)
    ).where(Loan.status == "on_loan").order_by(Loan.borrowed)

    results = stmt.all()
    return results

def get_prenotazioni(db: Session):
    stmt = (
        db.query(
            Book.title,
            Book.author,
            Loan.status,
            Copies.id,
            User.username,
            Loan.borrowed,
            Loan.due_back,
            Loan.return_date
            )
        .join(Copies, Copies.book_id == Book.id)
        .join(Loan, Loan.copies_id == Copies.id)
        .join(User, User.id == Loan.user_id)
    ).where(Loan.status == "booked").order_by(Loan.borrowed)

    results = stmt.all()
    return results

def booking_book(db: Session, id: str, current_user: str):
    db_book = db.query(Book).filter(Book.id == id).first()
    db_user = db.query(User).filter(User.username == current_user.username).first()
    db_copies = db.query(Copies).filter(Copies.id == id).first()
    giorno = datetime.now().date()
    load_data = schemas.LoanBase(
        copies_id = db_copies.id,
        user_id = db_user.id,
        borrowed = giorno,
        due_back = giorno + timedelta(days=30),
        status = "booked"
        )
    db_loan = Loan(**load_data.dict())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

def get_users(db: Session):
    return db.query(User).order_by(User.last_name.desc()).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: User):
    db.delete(user)
    db.commit()

def log_action(db, actor_id: int, action: str, target: str = None):
    log = models.AuditLog(
        actor_id=actor_id,
        action=action,
        target=target
    )
    db.add(log)
    db.commit()
