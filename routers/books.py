from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response, status
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import crud
import models
import schemas
from database import engine, get_db
from typing import Optional
from fastapi.responses import RedirectResponse, HTMLResponse

router = APIRouter(prefix="/books", tags=["Books"])
templates = Jinja2Templates(directory="templates")

# Render Add Book Page
@router.get("/add")
def add_book_page(request: Request, current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add_book.html", {
        "request": request,
        "current_user": current_user
    })

# Handle Book Creation from Web Form
@router.post("/add")
def create_book_web(
    request: Request,
    title: str=Form(...), 
    author: str=Form(...), 
    isbn: Optional[str]=Form(None),
    publisher: Optional[str]=Form(None),
    yearpubblish: Optional[str]=Form(None),
    release: Optional[str]=Form(None),
    language: Optional[str]=Form(None),
    description: Optional[str]=Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(crud.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    ## now = datetime.now()
    ## today = now.date()

    # Create book schema
    book_data = schemas.BookCreate(
        title = title, 
        author = author, 
        isbn = isbn,
        publisher = publisher,
        yearpubblish = yearpubblish,
        release = release,
        language = language,
        description = description
        )


    # Check if book already exists
    existing_book = crud.get_book_by_search(db, title,'titolo')
    if existing_book:
        return templates.TemplateResponse("add_book.html", {
            "request": request, 
            "error": "A book with this title already exists."
        })
    
    # Create book
    crud.create_book(db, book_data)

    return RedirectResponse("/", status_code=303)

# Modifica libro
@router.get("/edit/{book_id}")
def book_edit_page(
    request: Request, 
    book_id: str, 
    db: Session = Depends(get_db), 
    current_user: Optional[models.User] = Depends(crud.get_current_user)
):
    crud.require_role(current_user, ["admin"])

    book = crud.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(404)

    return templates.TemplateResponse(
        "book_edit.html",
        {
            "request": request,
            "book": book,
            "current_user": current_user
        }
    )

@router.post("/edit/{book_id}")
def book_edit_post(
    request: Request,
    id: str=Form(...),
    title: str=Form(...), 
    author: str=Form(...), 
    isbn: Optional[str]=Form(None),
    publisher: Optional[str]=Form(None),
    yearpubblish: Optional[int]=Form(0),
    release: Optional[str]=Form(None),
    language: Optional[str]=Form(None),
    description: Optional[str]=Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(crud.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    crud.require_role(current_user, ["admin","librarian"])

    book = crud.get_book_by_id(db, id)
    if not book:
        raise HTTPException(404)
    
    book.title = title, 
    book.author = author, 
    book.isbn = isbn,
    book.publisher = publisher,
    book.yearpubblish = yearpubblish,
    book.release = release,
    book.language = language,
    book.description = description
    
    db.commit()

    return RedirectResponse("/", status_code=303)

# Delete Book Endpoint
@router.get("/delete/{book_id}")
def delete_book_web(request: Request, book_id: str, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    delete_book(db, book_id)
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "books": get_books(db),
        "message": "Book deleted successfully!",
        "current_user": current_user
    })
