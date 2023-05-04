from typing import List

from fastapi import Depends, HTTPException, status, Path, Query, APIRouter
from fastapi_limiter.depends import RateLimiter
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


@router.get("/", response_model=List[ContactInListOutput],
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=2, seconds=5))])
async def get_contacts(filter_type: int = Query(default=0, ge=0, le=4),
                       filter_str: str | None = None,
                       _: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    """
    The get_contacts function returns a list of contacts.

    :param filter_type: int: Filter the contacts by type
    :param filter_str: str | None: Filter the contacts by name or phone number
    :param _: User: Get the current user from the auth_service
    :param db: Session: Pass the database session to the repository
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_cnt(db, filter_type, filter_str)
    return contacts


@router.get("/{cnt_id}", response_model=ContactOutput, dependencies=[Depends(allowed_operation_get)])
async def get_contact(cnt_id: int = Path(ge=1),
                      _: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)):
    """
    The get_contact function returns a contact by id.

    :param cnt_id: int: Get the contact id from the url
    :param _: User: Get the current user from the auth_service
    :param db: Session: Access the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_cnt_by_id(cnt_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact by id {cnt_id} not found")
    return contact


@router.post("/", response_model=ContactInListOutput, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_create), Depends(RateLimiter(times=1, seconds=10))])
async def create_contact(body: ContactInput,
                         _: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactInput object as input, which is validated by pydantic.
        If the validation fails, an HTTP 400 error is raised with details of what went wrong.

    :param body: ContactInput: Pass the contact information to be created
    :param _: User: Get the current user
    :param db: Session: Pass the database session to the repository layer
    :return: A contact object, which is a dictionary
    :doc-author: Trelent
    """
    try:
        contact = await repository_contacts.create_cnt(body, db)
    except exc.SQLAlchemyError as err:
        if db.in_transaction():
            db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.args[0])
    return contact


@router.put("/{cnt_id}", response_model=ContactInListOutput,
            dependencies=[Depends(allowed_operation_update), Depends(RateLimiter(times=1, seconds=10))],
            description='Only moderators and admin')
async def update_contact(body: ContactInput,
                         cnt_id: int = Path(ge=1),
                         _: User = Depends(auth_service.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The update_contact function updates a contact in the database.
        The function takes an id and a body as input, and returns the updated contact.
        If no contact is found with that id, it raises an HTTPException with status code 404 (Not Found).


    :param body: ContactInput: Define the input schema,
    :param cnt_id: int: Get the contact id from the url
    :param _: User: Get the current user from the auth_service
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
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
    """
    The delete_contact function deletes a contact from the database.
        The function takes in an id of the contact to be deleted and returns a 204 status code if successful.
        If no such contact exists, it returns 404 status code.

    :param cnt_id: int: Get the contact id from the path
    :param _: User: Make sure that the user is authenticated before they can delete a contact
    :param db: Session: Pass the database session to the repository layer
    :return: A contact object
    :doc-author: Trelent
    """
    try:
        contact = await repository_contacts.delete_cnt_by_id(cnt_id, db)
        if contact is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact by id {cnt_id} not found")
    except exc.SQLAlchemyError as err:
        if db.in_transaction():
            db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.args[0])
