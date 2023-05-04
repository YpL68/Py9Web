from fastapi import Depends, HTTPException, status, APIRouter, Security, BackgroundTasks, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from sqlalchemy.orm import Session

from src.conf import messages as msg
from src.database.db import get_db
from src.schemas import UserInput, TokenModel, RequestEmail, NewPasswordInput
from src. repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email, send_forgot_password

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/auth", tags=['auth'])
security = HTTPBearer()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(body: UserInput, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes a UserInput object as input, which contains the following fields:
            - email (required): The email address of the user to be created. Must be unique.
            - password (required): The password for this account, hashed using bcrypt before
              being stored in the database.

    :param body: UserInput: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base url of the application
    :param db: Session: Pass the database session to the repository_users
    :return: A dictionary with the detail key and a message as value
    :doc-author: Trelent
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg.ACCOUNT_ALREADY_EXISTS)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, EmailStr(new_user.email), new_user.username, str(request.base_url))
    return {"detail": msg.USER_SUCCESSFULLY_CREATED}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
        It takes in the username and password of the user, and returns an access token if successful.
        The access token can be used to make authenticated requests.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Get the database session
    :return: A dictionary with the access token, refresh token and the type of bearer
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg.INVALID_EMAIL)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg.EMAIL_NOT_CONFIRMED)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg.INVALID_PASSWORD)
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token_ = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token_, db)
    return {"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token, a new refresh_token, and the type of token.
        If there is no user with that email or if the user's current refresh_token does not match what was passed in,
        then it will return an error message.

    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param db: Session: Get the database session
    :return: A dictionary with the access_token, refresh_token and token_type
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg.INVALID_USER)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg.INVALID_REFRESH_TOKEN)

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token_ = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token_, db)
    return {"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"}


@router.post('/forgot_password', status_code=status.HTTP_200_OK)
async def forgot_password(body: RequestEmail, background_tasks: BackgroundTasks,
                          request: Request, db: Session = Depends(get_db)):
    """
    The forgot_password function is used to send a password reset email to the user.
        The function takes in an email address and sends a password reset link to that address.
        If the user does not exist, then an error message is returned.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A json object with a detail key and value
    :doc-author: Trelent
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg.INVALID_EMAIL)
    background_tasks.add_task(send_forgot_password, body.email, exist_user.username, str(request.base_url))
    return {"detail": msg.PASSWORD_RESET_SEND}


@router.get('/change_password/{token}', response_class=HTMLResponse, description="Change Password")
async def reset_password(token: str, request: Request, db: Session = Depends(get_db)):
    """
    The reset_password function is used to reset a user's password.
        It takes in the token from the email sent to the user, and then uses that token
        to get their email address. Then it gets their account information using that email address,
        and returns an HTML page with a form for them to change their password.

    :param token: str: Get the token from the url
    :param request: Request: Get the request object
    :param db: Session: Access the database
    :return: A templateresponse object
    :doc-author: Trelent
    """
    email = auth_service.get_email_from_token(token, "password_token")
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    return templates.TemplateResponse('password_change.html', {"request": request})


@router.put('/change_password/{token}')
async def change_password(token: str, body: NewPasswordInput, db: Session = Depends(get_db)):
    """
    The change_password function is used to change the password of a user.
        It takes in a token and body as parameters, where the token is used to verify that the user has access
        to change their password, and the body contains information about what they want their new password to be.


    :param token: str: Get the email from the token
    :param body: NewPasswordInput: Get the new password from the user
    :param db: Session: Get the database session
    :return: A dictionary with the key &quot;detail&quot; and value msg
    :doc-author: Trelent
    """
    email = auth_service.get_email_from_token(token, "password_token")
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg.VERIFICATION_ERROR)
    password = auth_service.get_password_hash(body.password)
    await repository_users.change_password(user, password, db)
    return {"detail": msg.PASSWORD_CHANGED}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes in the token that was sent to the user's email and uses it to get their email address.
        The function then checks if there is a user with that email, and if not, returns an error message.
        If there is a user with that email, it checks whether or not they have already confirmed their account.
        If they have already confirmed their account, it returns an error message saying so; otherwise,
        the function confirms the account by setting its 'confirmed' field to True.

    :param token: str: Get the email from the token
    :param db: Session: Connect to the database
    :return: A message that the email has been confirmed
    :doc-author: Trelent
    """
    email = auth_service.get_email_from_token(token, "email_token")
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg.VERIFICATION_ERROR)
    if user.confirmed:
        return {"detail": msg.EMAIL_CONFIRMED}
    await repository_users.confirmed_email(email, db)
    return {"detail": msg.EMAIL_CONFIRMED}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to confirm their account. The function takes in a RequestEmail object, which contains the email of
    the user who wants to confirm their account. It then checks if there is already an unconfirmed
    account associated with that email address, and if so it sends an email containing a confirmation link.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: Session: Get the database session
    :return: A message to the user
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        if user.confirmed:
            return {"message": msg.EMAIL_ALREADY_CONFIRMED}
        background_tasks.add_task(send_email, EmailStr(user.email), user.username, str(request.base_url))
    return {"detail": msg.CHECK_YOUR_EMAIL}
