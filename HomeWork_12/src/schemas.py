from datetime import datetime

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class ContactModel(BaseModel):
    first_name: str = Field(max_length=64)
    last_name: str = Optional[Field(max_length=64)]
    email: EmailStr = Field(max_length=64)
    birthday: datetime = Optional[datetime]
    address: str = Optional[Field(max_length=128)]
    phones: Optional[List[str]]

