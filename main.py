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
@app.get("/add-book")
def add_book_page(request: Request, current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add_book.html", {
        "request": request,
        "current_user": current_user
    })

# Handle Book Creation from Web Form
@app.post("/add-book")
def create_book_web(
    request: Request,
    operazione: str=Form(...),
    dataRitiro: str=Form(...),
    dataChiusura: str=Form(...),
    autore: str=Form(...), 
    titolo: str=Form(...), 
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(crud.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Create book schema
    book_data = schemas.BookCreate(
        operazione=operazione,
        dataRitiro=dataRitiro,
        dataChiusura=dataChiusura,
        autore=autore,
        titolo=titolo
        )


    # Check if book already exists
    existing_book = crud.get_book_by_titolo(db, titolo,'titolo')
    if existing_book:
        return templates.TemplateResponse("add_book.html", {
            "request": request, 
            "error": "A book with this title already exists."
        })
    
    # Create book
    create_book(db, book_data)

    # Conteggio totale dei record
    total = crud.get_books_count(db)
    
    # Calcolo del numero totale di pagine
    total_pages = (total + per_page - 1) // per_page

    
    # Redirect to home page
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "books": get_books(db),
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "message": "Book added successfully!",
        "current_user": current_user
    })

# Delete Book Endpoint
@app.get("/delete-book/{id}")
def delete_book_web(request: Request, id: str, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    delete_book(db, id)
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
