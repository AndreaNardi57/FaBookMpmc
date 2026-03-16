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
from datetime import datetime, date
from typing import Optional
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

router = APIRouter(prefix="/users", tags=["Users"])
templates = Jinja2Templates(directory="templates")

## User

@router.get("/")
def user_list(request: Request, db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(crud.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    crud.require_role(current_user, ["admin","librarian"])

    user = crud.get_users(db)
    return templates.TemplateResponse("users.html", {
        "request": request, 
        "users": user,
        "current_user": current_user
        })

@router.get("/add")
def user_add_page(
    request: Request,
    current_user: Optional[models.User] = Depends(crud.get_current_user)
):
    crud.require_role(current_user, ["admin"])

    return templates.TemplateResponse(
        "user_add.html",
        {"request": request, "current_user": current_user}
    )

@router.post("/add")
def user_add(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone: Optional[str] = Form(None),
    hashed_password: str = Form(...),
    role: Optional[str] = "user",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(crud.get_current_user)
):
    crud.require_role(current_user, ["admin"])

    hashed_password = auth.get_password_hash(hashed_password)

    new_user = models.User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone = phone if phone else None,
        hashed_password=hashed_password,
        role=role
    )

    crud.create_user(db, new_user)

    return RedirectResponse("/users", status_code=303)

@router.get("/modify")
def user_modify(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(crud.get_current_user)
):
    crud.require_role(current_user, ["user"])

    user = crud.get_user_by_id(db, current_user.id)
    if not user:
        raise HTTPException(404)

    return templates.TemplateResponse(
        "user_edit.html",
        {
            "request": request,
            "user": user,
            "current_user": current_user
        }
    )

@router.get("/edit/{user_id}")
def user_edit_page(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(crud.get_current_user)
):
    crud.require_role(current_user, ["admin"])

    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404)

    return templates.TemplateResponse(
        "user_edit.html",
        {
            "request": request,
            "user": user,
            "current_user": current_user
        }
    )

@router.post("/edit/{user_id}")
def user_edit(
    request: Request,
    user_id: int,
    email: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone: Optional[str] = Form(None),
    role: str = Form(...),
    is_active: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(crud.get_current_user)
):
    crud.require_role(current_user, ["admin"])
    
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404)

    # BLOCCO CRITICO
    if user.id == current_user.id:
        if role != current_user.role:
            raise HTTPException(
                status_code=400,
                detail="Non puoi cambiare il tuo ruolo"
            )
        if not is_active:
            raise HTTPException(
                status_code=400,
                detail="Non puoi disattivare il tuo account"
            )
    else:
        user.role = role
        user.is_active = True if is_active else False


    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.phone = phone if phone else None
    
    db.commit()

    crud.log_action(
        db,
        actor_id=current_user.id,
        action="MODIFICA_UTENTE",
        target=f"user_id={user.id}"
    )
    if current_user.role == "user":
        url = "/"
    else:
        url = "/users"

    return RedirectResponse(url, status_code=303)

@router.get("/delete/{user_id}")
def user_delete(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(crud.get_current_user)
):
    crud.require_role(current_user, ["admin"])

    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404)

    db.delete(user)
    db.commit()

    return RedirectResponse("/users", status_code=303)

@router.get("/{user_id}/password")
def change_user_password_page(
    request: Request,
    user_id: int,
    current_user: models.User = Depends(crud.get_current_user),
    db: Session = Depends(get_db)
):
    crud.require_role(current_user, ["admin"])

    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404)

    return templates.TemplateResponse(
        "user_password.html",
        {
            "request": request,
            "user": user,
            "current_user": current_user
        }
    )

@router.post("/{user_id}/password")
def change_user_password(
    user_id: int,
    password: str = Form(...),
    password_confirm: str = Form(...),
    current_user: models.User = Depends(crud.get_current_user),
    db: Session = Depends(get_db)
):
    crud.require_role(current_user, ["admin"])

    if password != password_confirm:
        raise HTTPException(status_code=400, detail="Le password non coincidono")

    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404)

    user.hashed_password = auth.get_password_hash(password)
    db.commit()

    return RedirectResponse("/users", status_code=303)

## Fine User
