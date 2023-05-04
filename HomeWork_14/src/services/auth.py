import pickle
from datetime import datetime, timedelta
from typing import Optional

# import redis as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer  # Bearer token
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.conf.config import settings
from src.database.db import get_db, redis_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the pwd_context object to verify that the
        plain-text password matches the hashed one.

        :param self: Represent the instance of the class
        :param plain_password: Check the password entered by the user
        :param hashed_password: Compare the hashed password in the database with the plain text password entered by user
        :return: A boolean value
        :doc-author: Trelent
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

        :param self: Represent the instance of the class
        :param password: str: Get the password from the user
        :return: A hashed password
        :doc-author: Trelent
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): A dictionary containing the claims to be encoded in the JWT.
                expires_delta (Optional[float]): An optional parameter specifying how long, in seconds,
                the access token should last before expiring. If not specified, it defaults to 15 minutes.

        :param self: Refer to the current object
        :param data: dict: Pass the data that will be encoded in the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: A jwt token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the token expires, defaults to None.

        :param self: Represent the instance of the class
        :param data: dict: Store the user's id and username
        :param expires_delta: Optional[float]: Set the expiration time of the refresh token
        :return: An encoded refresh token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the
            UserRouter class. It takes in a token and db as parameters, and returns
            the user object associated with that token. If no user is found, it raises
            an exception.

        :param self: Access the class attributes
        :param token: str: Pass the token to the function
        :param db: Session: Pass the database connection to the function
        :return: A user object
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await redis_db.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            await redis_db.set(f"user:{email}", pickle.dumps(user))
            await redis_db.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)

        return user

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.
        It takes a refresh_token as an argument and returns the email of the user if it's valid.
        If not, it raises an HTTPException with status code 401 (UNAUTHORIZED) and detail
        'Could not validate credentials'.


        :param self: Represent the instance of the class
        :param refresh_token: str: Pass the refresh token to the function
        :return: The email of the user who has logged in
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    def create_email_token(self, data: dict):
        """
        The create_email_token function takes a dictionary of data and returns a token.
        The token is encoded with the SECRET_KEY, which is set in the config file.
        The algorithm used to encode the token is also set in the config file.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that is to be encoded
        :return: A token that is encoded with the user's email address
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def get_email_from_token(self, token: str, scope: str):
        """
        The get_email_from_token function takes a token and scope as input. It then decodes the token using the SECRET_KEY
        and ALGORITHM defined in the class. If it is successful, it checks that the scope of this token matches what was
        passed to get_email_from_token. If so, it returns an email address from within this payload.

        :param self: Represent the instance of the class
        :param token: str: Pass in the token that is to be decoded
        :param scope: str: Check if the scope of the token is valid
        :return: The email address of the user associated with the token
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == scope:
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token.")

    def create_password_token(self, data: dict):
        """
        The create_password_token function creates a password token for the user.
            Args:
                data (dict): A dictionary containing the user's email and username.

        :param self: Make the function a method of the class
        :param data: dict: Pass the data to be encoded
        :return: A token which is encoded with the user's email, a timestamp and an expiry time
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=10)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "password_token"})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    def get_password_from_token(self, token: str):
        """
        The get_password_from_token function is used to decode the password token that was sent in the email.
        The function takes a token as an argument and returns the password if it is valid. If not, it raises an error.

        :param self: Represent the instance of the class
        :param token: str: Pass the token to this function
        :return: The password from the token
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'password_token':
                password = payload['sub']
                return password
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for password change")


auth_service = Auth()
