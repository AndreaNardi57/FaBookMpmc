from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response, status
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
import auth
import crud
import models
import schemas
from typing import Optional
from fastapi.responses import RedirectResponse, HTMLResponse

router = APIRouter(prefix="/helps", tags=["Helps"])
templates = Jinja2Templates(directory="templates")

@router.get("/user-guide")
def user_guide_page(request: Request, current_user: Optional[models.User] = Depends(crud.get_current_user)):
    return templates.TemplateResponse("user_guide.html", {
        "request": request,
        "current_user": current_user
    })

@router.get("/faq")
def faq_page(request: Request, current_user: Optional[models.User] = Depends(crud.get_current_user)):
    return templates.TemplateResponse("faq.html", {
        "request": request,
        "current_user": current_user
    })
