from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.db import get_db
from src.database.models import Contact

app = FastAPI()


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


@app.get("/")
async def main():
    return FileResponse("templates/index.html")


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
    contact.email = data["email"]
    contact.first_name = data["name"]
    db.commit()
    db.refresh(contact)
    return contact


@app.delete("/api/contacts/{id}")
def delete_contact(id, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == id).first()

    if contact is None:
        return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
    db.delete(contact)
    db.commit()
    return contact
