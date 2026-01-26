from sqlalchemy.orm import Session
from models.users import User
import schemas.users
from datetime import datetime
from sqlalchemy import or_

def get_user_by_search(db: Session, query: str,skip: int = 0,limit: int = 1000):
    return db.query(User).filter(or_(User.first_name.ilike(f"%{query}%"),User.last_name.ilike(f"%{query}%"),User.username.ilike(f"%{query}%"))).all()

def get_users_count_filtered(db: Session, query: str):
    return db.query(User).filter(or_(User.first_name.ilike(f"%{query}%"),User.last_name.ilike(f"%{query}%"),User.username.ilike(f"%{query}%"))).count()

def get_users(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(User).order_by(get_users.last_name.desc()).offset((skip-1)*limit).limit(limit).all()

def get_users_count(db: Session):
    return db.query(User).count()

def create_user(db: Session, book: schemas.BookCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_book(db: Session, id: str, book_update: schemas.BookCreate):
    db_user = db.query(Book).filter(Book.id == id).first()
    if db_user:
        for key, value in user_update.dict().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_book(db: Session, id: str):
    db_user = db.query(User).filter(User.id == id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


