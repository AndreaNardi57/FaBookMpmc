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
from routers import users, loans, helps, books


# Create the database tables
## models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="MPMC Library Management System")

app.include_router(users.router)
app.include_router(loans.router)
app.include_router(helps.router)
app.include_router(books.router)

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


# Add these to your main.py file, after the existing routes

@app.get("/about")
def about_page(request: Request, current_user: Optional[models.User] = Depends(crud.get_current_user)):
    return templates.TemplateResponse("about.html", {
        "request": request,
        "current_user": current_user
    })

@app.get("/contact")
def contact_page(request: Request, current_user: Optional[models.User] = Depends(crud.get_current_user)):
    return templates.TemplateResponse("contact.html", {
        "request": request,
        "current_user": current_user
    })


@app.get("/search")
def search_books(request: Request, query: str = "", search_field: str = "",  db: Session = Depends(get_db),page: int = 1,per_page: int = PerPage, current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Conteggio totale dei record
    total = crud.get_books_count_filtered(db,query,search_field)

    # Calcolo del numero totale di pagine
    total_pages = (total + per_page - 1) // per_page

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
