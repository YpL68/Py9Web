from sqlalchemy.orm import Session

from src.database.models import Contact, Phone
from src.schemas import ContactInput


async def get_cnt_by_id(cnt_id: int, db: Session):
    contact = db.query(Contact).get(cnt_id)
    return contact


async def get_cnt(db: Session):
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
