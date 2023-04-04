from fastapi import FastAPI, Depends, HTTPException, Body, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text, exc

from src.database.db import get_db
from src.database.models import Contact

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


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
async def root( request: Request, db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return templates.TemplateResponse("index.html", {"request": request, "filter_str": "1111", "contacts": contacts})


@app.get("/api/contacts")
async def get_contacts(db: Session = Depends(get_db)):
    return db.query(Contact).all()


@app.get("/api/contacts/{id}")
async def get_contact(id, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == id).first()
    if contact is None:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
    return contact


@app.post("/api/contacts")
def create_contact(data=Body(), db: Session = Depends(get_db)):
    contact = Contact(first_name=data["name"], email=data["email"])
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
    print(contact.full_name)
    return contact


@app.delete("/api/contacts/{id}")
def delete_contact(id, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == id).first()

    if contact is None:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
    db.delete(contact)
    db.commit()
    return contact
