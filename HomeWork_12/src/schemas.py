from datetime import date

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

from src.database.models import Role


class PhoneOutput(BaseModel):
    phone_num: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "phone_num": "380972547845",
            }
        }


class ContactInput(BaseModel):
    first_name: str = Field()
    last_name: Optional[str]
    email: EmailStr
    birthday: Optional[date] = None
    address: Optional[str] = None
    phones: Optional[List[PhoneOutput]] = []

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Ben",
                "last_name": "Smith",
                "email": "example@example.ua",
                "birthday": "1968-12-01",
                "address": "1, Hlazunova Street Kyiv - 42, Ukraine, 01601",
                "phones": [{"phone_num": "380972547845"}]
            }
        }


class ContactOutput(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    email: str
    birthday: Optional[date] = None
    address: Optional[str] = None
    phones: Optional[List[PhoneOutput]] = []

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "first_name": "Ben",
                "last_name": "Smith",
                "email": "example@example.ua",
                "birthday": "1968-12-01",
                "address": "1, Hlazunova Street Kyiv - 42, Ukraine, 01601",
                "phones": [{"phone_num": "380972547845"}]
            }
        }


class ContactInListOutput(BaseModel):
    id: int
    full_name: str
    email: str
    birthday: Optional[date] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "full_name": "Ben Smith",
                "email": "example@example.ua",
                "birthday": "1968-12-01",
            }
        }


class UserInpur(BaseModel):
    username: str = Field(min_length=6, max_length=12)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserOutput(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    roles: Role

    class Config:
        orm_mode = True
