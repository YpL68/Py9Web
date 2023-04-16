from typing import List

from fastapi import Depends, HTTPException, status, Path, APIRouter
from sqlalchemy import exc
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import contacts as repository_contacts
from src.schemas import ContactInput, ContactOutput, ContactInListOutput


router = APIRouter(prefix="/contacts", tags=['contacts'])


@router.get("/", response_model=List[ContactInListOutput], tags=["contacts"])
async def get_contacts(db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_cnt(db)
    return contacts


@router.get("/{cnt_id}", response_model=ContactOutput)
async def get_contact(cnt_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = await repository_contacts.get_cnt_by_id(cnt_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact by id {cnt_id} not found")
    return contact


@router.post("/", response_model=ContactOutput, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactInput, db: Session = Depends(get_db)):
    try:
        contact = await repository_contacts.create_cnt(body, db)
    except exc.IntegrityError as err:
        if db.in_transaction():
            db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.orig.args[0])
    return contact


@router.delete("/{cnt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(cnt_id: int = Path(ge=1), db: Session = Depends(get_db)):
    try:
        contact = await repository_contacts.delete_cnt_by_id(cnt_id, db)
        if contact is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact by id {cnt_id} not found")
    except exc.IntegrityError as err:
        if db.in_transaction():
            db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.orig.args[0])


@router.put("/{cnt_id}", response_model=ContactInListOutput)
async def update_contact(body: ContactInput, cnt_id: int = Path(ge=1), db: Session = Depends(get_db)):
    try:
        contact = await repository_contacts.update_cnt(cnt_id, body, db)
        if contact is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact by id {cnt_id} not found")
    except exc.IntegrityError as err:
        if db.in_transaction():
            db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err.orig.args[0])
    return contact
