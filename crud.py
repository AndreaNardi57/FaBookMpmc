from fastapi import Depends, Request, HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from sqlalchemy import and_
## from models import Book
## from schemas import BookCreate
import models
import schemas
import crud
from models import Book, Copies, User, Loan
from schemas import BookCreate

from datetime import datetime, timedelta
from sqlalchemy import or_

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> Optional[models.User]:
    username = request.cookies.get("mpmc_user")
    if not username:
        return None
    result = db.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()

def require_role(user, allowed_roles: list[str]):
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permesso negato"
        )

def get_book_by_search(db: Session, query: str,search_field: str,skip: int = 0,limit: int = 1000):
    if search_field == "title":
        return db.query(Book).filter(Book.title.ilike(f"%{query}%")).order_by(Book.author.desc()).offset(skip).limit(limit).all()
    elif search_field == "author":
        return db.query(Book).filter(Book.author.ilike(f"%{query}%")).order_by(Book.author.desc()).offset(skip).limit(limit).all()

def get_books_count_filtered(db: Session, query: str, search_field: str):
    if search_field == "title":
        return db.query(Book).filter(Book.title.ilike(f"%{query}%")).count()
    elif search_field == "author":
        return db.query(Book).filter(Book.author.ilike(f"%{query}%")).count()

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

def get_book_by_id(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()

def get_loans(db: Session, id=None):
    query_filter = []
    if id:
        query_filter.append(User.id == id)
    stmt = (
        db.query(
            Loan.id,
            Book.title,
            Book.author,
            Loan.status,
            Copies.id.label('cp_id'),
            User.username,
            Loan.borrowed,
            Loan.due_back,
            Loan.return_date
            )
        .join(Copies, Copies.book_id == Book.id)
        .join(Loan, Loan.copies_id == Copies.id)
        .join(User, User.id == Loan.user_id)
    ).filter(*query_filter).order_by(Loan.borrowed)
    

    results = stmt.all()
    return results

def get_loans_by_id(db: Session, id: str):
    stmt = (
        db.query(
            Loan.id,
            Book.title,
            Book.author,
            Loan.status,
            Copies.id.label('cp_id'),
            User.username,
            Loan.borrowed,
            Loan.due_back,
            Loan.return_date
            )
        .join(Copies, Copies.book_id == Book.id)
        .join(Loan, Loan.copies_id == Copies.id)
        .join(User, User.id == Loan.user_id)
    ).filter(Loan.id == id)

    results = stmt.first()
    return results

def get_loans_lst(db: Session, id=None):
    query_filter = []
    if id:
        query_filter.append(User.id == id)
    
    stmt = (
        db.query(
            Loan.id,
            Book.title,
            Book.author,
            Loan.status,
            Copies.id.label('cp_id'),
            User.username,
            Loan.borrowed,
            Loan.due_back,
            Loan.return_date
            )
        .join(Copies, Copies.book_id == Book.id)
        .join(Loan, Loan.copies_id == Copies.id)
        .join(User, User.id == Loan.user_id)
    ).filter(Loan.status == "on_loan").filter(*query_filter).order_by(Loan.borrowed)
    
    results = stmt.all()
    return results

def get_prenotazioni(db: Session, id=None):
    query_filter = []
    if id:
        query_filter.append(User.id == id)
    
    stmt = (
        db.query(
            Loan.id,
            Book.title,
            Book.author,
            Loan.status,
            Copies.id.label('cp_id'),
            User.username,
            Loan.borrowed,
            Loan.due_back,
            Loan.return_date
            )
        .join(Copies, Copies.book_id == Book.id)
        .join(Loan, Loan.copies_id == Copies.id)
        .join(User, User.id == Loan.user_id)
    ).filter(Loan.status == "booked").filter(*query_filter).order_by(Loan.borrowed)
    
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


def get_available_copy(db: Session, book_id: int):
    
    copies = db.query(Copies).filter(Copies.book_id == book_id).all()

    for copy in copies:
        active_loan = db.query(Loan).filter(
            Loan.copies_id == copy.id,
            Loan.status == "on_loan"
        ).first()

        if not active_loan:
            return copy

    return None
