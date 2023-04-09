from datetime import date

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class ContactResponse(BaseModel):
    id: int
    first_name: str = Field(title="Contact first name", max_length=64)
    last_name: str = Field(default=None, max_length=64)
    email: Optional[EmailStr] = None
    birthday: Optional[date] = None
    # address: str
    # phones: List[str] = []

    class Config:
        orm_mode = True
