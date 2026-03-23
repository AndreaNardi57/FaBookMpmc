from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response, status
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
from routers import users, loans


# Create the database tables
## models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="MPMC Library Management System")

app.include_router(users.router)
app.include_router(loans.router)

# Setup templates and static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
PerPage = 15
page = 1


# Render Home Page
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db),page: int = page,per_page: int = PerPage, current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # Conteggio totale dei record
    total = crud.get_books_count(db)
    
    books = crud.get_books(db,page,per_page)
    
    # Calcolo del numero totale di pagine
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "books": books,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "current_user": current_user
    })

# Render Add Book Page
@app.get("/book/add")
def add_book_page(request: Request, current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add_book.html", {
        "request": request,
        "current_user": current_user
    })

# Handle Book Creation from Web Form
@app.post("/book/add")
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

# Modifica il libro
##@app.get("/book/modify")
##def book_mod_page(
##    request: Request,
##    db: Session = Depends(get_db),
##    page: int = page,
##    per_page: int = PerPage,
##    current_user: Optional[models.User] = Depends(crud.get_current_user)
##):
##
##    if not current_user:
##        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
##    crud.require_role(current_user, ["admin"])
##
##    # Conteggio totale dei record
##    total = crud.get_books_count(db)
##
##    books = crud.get_books(db,page,per_page)
##
##    # Calcolo del numero totale di pagine
##    total_pages = (total + per_page - 1) // per_page
##
##    return templates.TemplateResponse("book_mod.html", {
##        "request": request,
##        "books": books,
##        "page": page,
##        "per_page": per_page,
##        "total_pages": total_pages,
##        "current_user": current_user
##    })

# Modifica libro
@app.get("/book/edit/{book_id}")
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

@app.post("/book/edit/{book_id}")
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
@app.get("/book/delete/{book_id}")
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

# Add these to your main.py file, after the existing routes

@app.get("/about")
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {
        "request": request
    })

@app.get("/contact")
def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {
        "request": request
    })

@app.get("/help/user-guide")
def user_guide_page(request: Request):
    return templates.TemplateResponse("user_guide.html", {
        "request": request
    })

@app.get("/help/faq")
def faq_page(request: Request):
    return templates.TemplateResponse("faq.html", {
        "request": request
    })

@app.get("/search")
def search_books(request: Request, query: str = "", search_field: str = "",  db: Session = Depends(get_db),page: int = 1,per_page: int = PerPage, current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Conteggio totale dei record
    #total = crud.get_books_count_filtered(db,query)

    # Calcolo del numero totale di pagine
    #total_pages = (total + per_page - 1) // per_page

    books = crud.get_book_by_search(db, query,search_field)
    return templates.TemplateResponse("filtered.html", {
        "request": request, 
        "books": books,
       "current_user": current_user
        })


# --- LOGIN ---
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login/html")
async def login_user(
    response: Response,
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = db.execute(select(models.User).where(models.User.username == username))
    user = result.scalar_one_or_none()

    ## if user.role == 'beginner':
    ##    return templates.TemplateResponse("login.html", {"request": request, "error": "L'utente deve essere registrato da un amministratore."})

    if not user or not user.is_active or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password or user disabled"})

    # Use a cookie to implement a simple session
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="mpmc_user", value=user.username, httponly=True)
    return response

# --- LOGOUT ---
@app.get("/logout")
async def logout_user(response: Response):
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="mpmc_user")
    return response

# Running the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
