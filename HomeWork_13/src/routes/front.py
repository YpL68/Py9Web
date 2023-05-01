from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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
