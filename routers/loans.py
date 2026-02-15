from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response, status
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
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
