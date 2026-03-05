from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response, status
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy import update
import auth
import crud
import models
import schemas
from database import engine, get_db
from datetime import datetime
from typing import Optional
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

router = APIRouter(prefix="/loans", tags=["Loans"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
def loan_books(request: Request, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    loans = crud.get_loans(db)
    return templates.TemplateResponse("prestiti.html", {
        "request": request, 
        "loans": loans,
        "current_user": current_user
        })

@router.get("/list")
def loan_lst(request: Request, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    loans = crud.get_loans_lst(db)
    return templates.TemplateResponse("prestiti.html", {
        "request": request, 
        "loans": loans,
        "current_user": current_user,
        "flag": "true"
        })

@router.get("/booking")
def prenoto(request: Request, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    loans = crud.get_prenotazioni(db)
    return templates.TemplateResponse("prestiti.html", {
        "request": request, 
        "loans": loans,
        "current_user": current_user,
        "flag": "true"
        })

# Booking Book Endpoint
@router.get("/booking/{id}")
def booking_web(request: Request, id: str, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    crud.booking_book(db, id, current_user)
    return RedirectResponse(url="/")
    ## return templates.TemplateResponse("index.html", {
    ##    "request": request, 
    ##    "books": crud.get_books(db),
    ##    "message": "Book returned successfully!",
    ##    "current_user": current_user
    ## })


@router.get("/edit/{id}")
def edit_loan(request: Request, id: int, db: Session = Depends(get_db), current_user: models.User = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    crud.require_role(current_user, ["admin","librarian"])

    qloans = crud.get_loans_by_id(db, id)

    return templates.TemplateResponse("loan_edit.html",{
        "request": request, 
        "qloans": qloans,
        "current_user": current_user
        })

@router.post("/edit/{id}")
def post_edit_loan(
    request: Request, id: int,
    status: str = Form(...),
    borrowed: str = Form(...),
    due_back: str = Form(...),
    return_date: str = Form(...),
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(crud.get_current_user)
):
    crud.require_role(current_user, ["admin", "librarian"])
    loan_query = db.query(models.Loan).filter(models.Loan.id==id).first()

    db.query(models.Loan).filter(models.Loan.id == id).update({"status": status, "borrowed": borrowed, "due_back": due_back, "return_date": return_date})


    ## new_loan = models.Loan(
    ##    copies_id = loan_query.copies_id,
    ##    user_id = loan_query.user_id,
    ##    status = status,
    ##    borrowed = borrowed,
    ##    due_back = due_back,
    ##    return_date = return_date
    ##)

    ## db.update(new_loan)
    db.commit()

    return RedirectResponse("/", status_code=303)

@router.get("/new")
def new_loan_page(
    request: Request,
    book_query: str = "",
    user_query: str = "",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(crud.get_current_user)
):
    crud.require_role(current_user, ["admin", "librarian"])

    books_query = db.query(models.Book)
    if book_query:
        books_query = books_query.filter(models.Book.title.ilike(f"%{book_query}%"))

    users_query = db.query(models.User).filter(models.User.is_active == True)
    if user_query:
        users_query = users_query.filter(models.User.username.ilike(f"%{user_query}%"))

    return templates.TemplateResponse(
        "loan_new.html",
        {
            "request": request,
            "books": books_query.limit(20).all(),
            "users": users_query.limit(20).all(),
            "current_user": current_user
        }
    )


@router.post("/new")
def create_loan(
    book_id: int = Form(...),
    user_id: int = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(crud.get_current_user)
):
    crud.require_role(current_user, ["admin", "librarian"])

    # 🔎 Trova copia disponibile
    copy = crud.get_available_copy(db, book_id)

    if not copy:
        flash_message = "Nessuna copia disponibile per questo libro."
        return templates.TemplateResponse(
            "loan_new.html",
            {
                "request": request,
                "books": db.query(models.Book).all(),
                "users": db.query(models.User).filter(models.User.is_active == True).all(),
                "error": flash_message,
                "current_user": current_user
            }
        )

    new_loan = models.Loan(
        book_id = book_id,
        user_id = user_id,
        status = status,
        borrowed = datetime.utcnow(),
        due_back = datetime.utcnow() + timedelta(days=30),
    )

    db.add(new_loan)
    db.commit()

    return RedirectResponse("/", status_code=303)