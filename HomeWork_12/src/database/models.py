import enum

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date, func, Enum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from src.functions import sanitize_phone_num

Base = declarative_base()


class MyBaseModel(Base):
    __abstract__ = True
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    created_on = Column(DateTime, nullable=False, default=func.now())
    updated_on = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class Contact(MyBaseModel):
    __tablename__ = "contacts"
    first_name = Column(String(64), index=True, nullable=False)
    last_name = Column(String(64))

    @hybrid_property
    def full_name(self):
        return f"{self.first_name}{' ' + self.last_name if self.last_name else ''}"

    def birth_day(self):

        return f"{self.first_name}{' ' + self.last_name if self.last_name else ''}"

    email = Column(String(64), unique=True, nullable=False)
    birthday = Column(Date)

    address = Column(String(128))
    phones = relationship("Phone", cascade="all, delete-orphan", back_populates="contact")


class Phone(MyBaseModel):
    __tablename__ = "phones"
    contact_id = Column(None, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    phone_num = Column(String(12), nullable=False, index=True, unique=True)
    contact = relationship("Contact", back_populates="phones")

    def __int__(self, contact_id: int, phone_num: str):
        self.contact_id = contact_id
        self.phone_num = sanitize_phone_num(phone_num)


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(MyBaseModel):
    __tablename__ = "users"
    username = Column(String(12), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    roles = Column('roles', Enum(Role), default=Role.user)
