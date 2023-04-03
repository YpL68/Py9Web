from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from src.functions import sanitize_phone_num

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    created_on = Column(DateTime, nullable=False, default=func.now())
    updated_on = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class Contact(BaseModel):
    __tablename__ = "contacts"
    first_name = Column(String(64), index=True, nullable=False)
    last_name = Column(String(64))

    @hybrid_property
    def full_name(self):
        return self.first_name + (f" {self.last_name}" if self.last_name else "")

    email = Column(String(64), unique=True)
    birthday = Column(DateTime)
    address = Column(String(128))
    phones = relationship("Phone", cascade="all, delete-orphan", back_populates="contact")


class Phone(BaseModel):
    __tablename__ = "phones"
    contact_id = Column(None, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    phone_num = Column(String(12), nullable=False, index=True, unique=True)
    contact = relationship("Contact", back_populates="phones")

    def __int__(self, contact_id: int, phone_num: str):
        self.contact_id = contact_id
        self.phone_num = sanitize_phone_num(phone_num)
