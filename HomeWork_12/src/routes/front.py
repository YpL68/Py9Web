from fastapi import Depends, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository.contacts import get_cnt
from src.services.auth import auth_service

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=['front'])


def format_date(value):
    if value is None:
        return ""
    return value.strftime("%d.%m.%Y")


templates.env.filters["format_date"] = format_date


@router.get("/", response_class=HTMLResponse, description="Main Page")
async def root(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})


@router.get("/contacts", response_class=HTMLResponse, description="Contacts Page")
async def contacts(request: Request):
    return templates.TemplateResponse("contacts.html", {"request": request})
