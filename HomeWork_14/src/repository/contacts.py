from datetime import date, timedelta
from typing import Type

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from src.database.models import Contact, Phone
from src.schemas import ContactInput


async def get_cnt_by_id(cnt_id: int, db: Session) -> Contact:
    """
    The get_cnt_by_id function returns a contact by its id.
        Args:
            cnt_id (int): The id of the contact to be returned.
            db (Session): A database session object that is used to query the database for contacts.

    :param cnt_id: int: Get the contact with the given id
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).get(cnt_id)
    await get_birth_list(db)
    return contact


async def get_cnt(db: Session, filter_type: int = 0, filter_str: str = None) -> list[Type[Contact]]:
    """
    The get_cnt function is used to retrieve a list of contacts from the database.
        The function accepts two parameters: filter_type and filter_str.  If no parameters are passed,
        all contacts in the database will be returned in alphabetical order by first name and last name.

    :param db: Session: Pass the database session to the function
    :param filter_type: int: Filter the contacts by first name, last name, email or birthday
    :param filter_str: str: Filter the contacts based on a string
    :return: A list of contacts
    :doc-author: Trelent
    """
    if filter_type == 4:
        contacts = await get_birth_list(db)
    else:
        if filter_str:
            filter_str = f"%{filter_str}%"
        else:
            filter_type = 0

        match filter_type:
            case 1:
                contacts = db.query(Contact).filter(Contact.first_name.ilike(filter_str)).\
                    order_by(Contact.first_name, Contact.last_name).all()
            case 2:
                contacts = db.query(Contact).filter(Contact.last_name.ilike(filter_str)).\
                    order_by(Contact.first_name, Contact.last_name).all()
            case 3:
                contacts = db.query(Contact).filter(Contact.email.ilike(filter_str)).\
                    order_by(Contact.first_name, Contact.last_name).all()
            case _:
                contacts = db.query(Contact).order_by(Contact.first_name, Contact.last_name).all()
    return contacts


async def create_cnt(body: ContactInput, db: Session) -> Contact:
    """
    The create_cnt function creates a new contact in the database.

    :param body: ContactInput: Validate the input data
    :param db: Session: Access the database
    :return: A contact object, which is the same type as the return value of get_cnt
    :doc-author: Trelent
    """
    contact = Contact()
    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.birthday = body.birthday
    contact.email = body.email
    contact.address = body.address
    db.add(contact)

    if body.phones:
        for phone_ in body.phones:
            db.add(Phone(phone_num=phone_.phone_num, contact=contact))

    db.commit()
    db.refresh(contact)
    return contact


async def update_cnt(cnt_id: int, body: ContactInput, db: Session) -> Contact | None:
    """
    The update_cnt function updates a contact in the database.
        Args:
            cnt_id (int): The id of the contact to update.
            body (ContactInput): The updated information for the contact.

    :param cnt_id: int: Identify the contact to be deleted
    :param body: ContactInput: Pass the data from the request body to update_cnt function
    :param db: Session: Pass the database session to the function
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await get_cnt_by_id(cnt_id, db)
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.birthday = body.birthday
        contact.email = body.email
        contact.address = body.address

        if body.phones:
            new_list_phones = [phone.phone_num for phone in body.phones]
            for phone_cnt in contact.phones:
                if phone_cnt.phone_num in new_list_phones:
                    new_list_phones.remove(phone_cnt.phone_num)
                else:
                    db.delete(phone_cnt)

            if new_list_phones:
                contact.phones.extend([Phone(phone_num=p_num, contact=contact) for p_num in new_list_phones])
                # new_phones = []
                # for p_num in new_list_phones:
                #     new_phones.append(Phone(phone_num=p_num, contact=contact))
        db.commit()
    return contact


async def delete_cnt_by_id(cnt_id: int, db: Session) -> Contact | None:
    """
    The delete_cnt_by_id function deletes a contact from the database by its id.
        Args:
            cnt_id (int): The id of the contact to be deleted.
            db (Session): A connection to the database.

    :param cnt_id: int: Specify the id of the contact to be deleted
    :param db: Session: Pass the database session to the function
    :return: The deleted contact or none if the contact doesn't exist
    :doc-author: Trelent
    """
    contact = await get_cnt_by_id(cnt_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_birth_list(db: Session) -> list[Type[Contact]]:
    """
    The get_birth_list function returns a list of contacts whose birthday is within the next 7 days.
    The function takes in a database session and uses it to query the Contact table for all contacts
    whose birthday falls between today's date and seven days from now. The results are ordered by
    birthday.

    :param db: Session: Pass the database session to the function
    :return: A list of contacts whose birthday is in the next 7 days
    :doc-author: Trelent
    """
    date_today_dof = date.today().timetuple().tm_yday
    date_end_dof = (date.today() + timedelta(days=7)).timetuple().tm_yday
    if date_end_dof > date_today_dof:
        contacts = db.query(Contact).\
            filter(func.date_part('doy', Contact.birthday).between(date_today_dof, date_end_dof)).\
            order_by(Contact.birthday).all()
    else:
        contacts = db.query(Contact).\
            filter(or_(func.date_part('doy', Contact.birthday).between(date_today_dof, 366),
                       func.date_part('doy', Contact.birthday).between(1, date_end_dof))).\
            order_by(Contact.birthday).all()
    return contacts
