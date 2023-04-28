from typing import List

from fastapi import Depends, HTTPException, status, Path, Query, APIRouter
from sqlalchemy import exc
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import contacts as repository_contacts
from src.schemas import ContactInput, ContactOutput, ContactInListOutput
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix="/contacts", tags=['contacts'])

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator])
allowed_operation_remove = RoleAccess([Role.admin])


@router.get("/", response_model=List[ContactInListOutput], dependencies=[Depends(allowed_operation_get)])
async def get_contacts(filter_type: int = Query(default=0, ge=0, le=4),
                       filter_str: str | None = None,
                       _: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_cnt(db, filter_type, filter_str)
    return contacts


@router.get("/{cnt_id}", response_model=ContactOutput, dependencies=[Depends(allowed_operation_get)])
async def get_contact(cnt_id: int = Path(ge=1),
                      _: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):
    contact = await repository_contacts.get_cnt_by_id(cnt_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact by id {cnt_id} not found")
    return contact


@router.post("/", response_model=ContactInListOutput, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_create)])
async def create_contact(body: ContactInput,
                         _: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    try:
        contact = await repository_contacts.create_cnt(body, db)
    except exc.SQLAlchemyError as err:
        if db.in_transaction():
            db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.args[0])
    return contact


@router.put("/{cnt_id}", response_model=ContactInListOutput, dependencies=[Depends(allowed_operation_update)],
            description='Only moderators and admin')
async def update_contact(body: ContactInput,
                         cnt_id: int = Path(ge=1),
                         _: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    try:
        contact = await repository_contacts.update_cnt(cnt_id, body, db)
        if contact is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact by id {cnt_id} not found")
    except exc.SQLAlchemyError as err:
        if db.in_transaction():
            db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.args[0])
    return contact


@router.delete("/{cnt_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allowed_operation_remove)],
               description='Only admin')
async def delete_contact(cnt_id: int = Path(ge=1),
                         _: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    try:
        contact = await repository_contacts.delete_cnt_by_id(cnt_id, db)
        if contact is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact by id {cnt_id} not found")
    except exc.SQLAlchemyError as err:
        if db.in_transaction():
            db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.args[0])
