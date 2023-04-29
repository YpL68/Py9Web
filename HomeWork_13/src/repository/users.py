from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserInput


async def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserInput, db: Session):
    g = Gravatar(body.email)

    new_user = User()
    new_user.username = body.username
    new_user.email = body.email
    new_user.password = body.password
    new_user.avatar = g.get_image()

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
