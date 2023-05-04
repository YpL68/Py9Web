from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserInput


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email if it exists. If no such user exists,
    it returns None.

    :param email: str: Specify the email address of the user
    :param db: Session: Pass in the database session to the function
    :return: The first user with a matching email address
    :doc-author: Trelent
    """
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserInput, db: Session) -> User:
    """
    The create_user function creates a new user in the database.

    :param body: UserInput: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
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


async def update_token(user: User, refresh_token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user in the database
    :param refresh_token: str | None: Specify the type of the refresh_token parameter
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Specify the email of the user to be confirmed
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def change_password(user: User, password: str, db: Session) -> None:
    """
    The change_password function takes a user and password, then updates the user's password in the database.

    :param user: User: Pass in the user object
    :param password: str: Pass in the new password
    :param db: Session: Pass the database session to the function
    :return: None, which means that it doesn't return anything
    :doc-author: Trelent
    """
    user.password = password
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: str: Get the user by email
    :param url: str: Pass in the url of the avatar to be updated
    :param db: Session: Pass the database session to the function
    :return: The updated user
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
