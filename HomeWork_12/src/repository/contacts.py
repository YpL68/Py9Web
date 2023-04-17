from datetime import date
from dateutil.relativedelta import relativedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from src.database.models import Contact, Phone
from src.schemas import ContactInput


async def get_cnt_by_id(cnt_id: int, db: Session):
    contact = db.query(Contact).get(cnt_id)
    await get_birth_list(db)
    return contact


async def get_cnt(db: Session, filter_type: int = 0, filter_str: str = None):
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


async def create_cnt(body: ContactInput, db: Session):
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


async def update_cnt(cnt_id: int, body: ContactInput, db: Session):
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


async def delete_cnt_by_id(cnt_id: int, db: Session):
    contact = await get_cnt_by_id(cnt_id, db)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def get_birth_list(db: Session):
    date_today_dof = date.today().timetuple().tm_yday
    date_end_dof = (date.today() + relativedelta(days=7)).timetuple().tm_yday
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
