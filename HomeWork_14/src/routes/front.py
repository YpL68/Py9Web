from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=['front'])


def format_date(value):
    """
    The format_date function takes a datetime object and returns a string in the format dd.mm.yyyy.

    :param value: Pass the value of the field to be formatted
    :return: A string in the format dd.mm.yyyy
    :doc-author: Trelent
    """
    if value is None:
        return ""
    return value.strftime("%d.%m.%Y")


templates.env.filters["format_date"] = format_date


@router.get("/", response_class=HTMLResponse, description="Main Page")
async def root(request: Request):
    """
    The root function is the entry point for the web application.
    It returns a TemplateResponse object, which renders an HTML template using Jinja2.
    The template is located in templates/index.html and uses data from request to render itself.

    :param request: Request: Get the request object for the current request
    :return: A template response object which is a subclass of response
    :doc-author: Trelent
    """
    return templates.TemplateResponse('index.html', {"request": request})


@router.get("/contacts", response_class=HTMLResponse, description="Contacts Page")
async def contacts(request: Request):
    """
    The contacts function is a view callable which returns an HTML page with the contact information.

    :param request: Request: Get the request object
    :return: The contacts
    :doc-author: Trelent
    """
    return templates.TemplateResponse("contacts.html", {"request": request})
