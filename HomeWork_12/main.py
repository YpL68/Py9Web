from typing import List

from fastapi import FastAPI, Depends, HTTPException, Body, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.db import get_db
from src.database.models import Contact
from src.schemas import ContactResponse, ContactListResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def format_date(value):
    if value is None:
        return ""
    return value.strftime("%d.%m.%Y")


templates.env.filters["format_date"] = format_date


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": f"{request.url}: {str(exc)}"}
    )


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if db.in_transaction():
            db.commit()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=e.detail)
    except Exception:
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/contacts", response_class=HTMLResponse)
async def contacts(request: Request, db: Session = Depends(get_db)):
    data = db.query(Contact.id,
                    Contact.full_name,
                    Contact.birthday,
                    Contact.email)\
        .order_by(Contact.first_name, Contact.last_name).all()
    return templates.TemplateResponse("contacts.html", {"request": request, "filter_str": "", "contacts": data})


@app.get("/api/contacts", response_model=List[ContactListResponse])
async def get_contacts(db: Session = Depends(get_db)):
    return db.query(Contact.id,
                    Contact.full_name,
                    Contact.birthday,
                    Contact.email)\
        .order_by(Contact.first_name, Contact.last_name).all()


@app.get("/api/contacts/{cnt_id}", response_model=ContactResponse)
async def get_contact(cnt_id, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == cnt_id).first()
    if contact is None:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
    return contact


# @app.get("/api/contacts/{cnt_id}")
# async def get_contact(cnt_id, db: Session = Depends(get_db)):
#     contact = db.query(Contact.id, Contact.phones).filter(Contact.id == cnt_id).first()
#     if contact is None:
#         return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
#     return contact


@app.post("/api/contacts")
def create_contact(data=Body(), db: Session = Depends(get_db)):
    contact = Contact()
    contact.first_name = data["first_name"]
    contact.last_name = data["last_name"] if data["last_name"] else None
    contact.birthday = data["birthday"] if data["birthday"] else None
    contact.email = data["email"]
    contact.address = data["address"] if data["address"] else None
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@app.put("/api/contacts")
def edit_contact(data=Body(), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == data["id"]).first()
    if contact is None:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
    contact.first_name = data["first_name"]
    contact.last_name = data["last_name"] if data["last_name"] else None
    contact.birthday = data["birthday"] if data["birthday"] else None
    contact.email = data["email"]
    contact.address = data["address"] if data["address"] else None
    try:
        db.commit()
    except Exception as err:
        if db.in_transaction():
            db.rollback()
        return JSONResponse(status_code=500, content={"message": str(err)})
    db.refresh(contact)
    return contact


@app.delete("/api/contacts/{cnt_id}")
def delete_contact(cnt_id, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == cnt_id).first()

    if contact is None:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
    db.delete(contact)
    db.commit()
    return contact
