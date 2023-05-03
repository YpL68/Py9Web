from fastapi import Depends, HTTPException, status, APIRouter, Security, BackgroundTasks, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from sqlalchemy import exc
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
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg.ACCOUNT_ALREADY_EXISTS)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return {"detail": msg.USER_SUCCESSFULLY_CREATED}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg.INVALID_EMAIL)
    background_tasks.add_task(send_forgot_password, body.email, exist_user.username, str(request.base_url))
    return {"detail": msg.PASSWORD_RESET_SEND}


@router.get('/change_password/{token}', response_class=HTMLResponse, description="Change Password")
async def reset_password(token: str, request: Request, db: Session = Depends(get_db)):
    email = auth_service.get_email_from_token(token, "password_token")
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    return templates.TemplateResponse('password_change.html', {"request": request})


@router.put('/change_password/{token}')
async def change_password(token: str, body: NewPasswordInput, db: Session = Depends(get_db)):
    email = auth_service.get_email_from_token(token, "password_token")
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg.VERIFICATION_ERROR)
    password = auth_service.get_password_hash(body.password)
    try:
        await repository_users.change_password(user, password, db)
    except exc.SQLAlchemyError as err:
        if db.in_transaction():
            db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.args[0])
    return {"detail": msg.PASSWORD_CHANGED}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
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
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        if user.confirmed:
            return {"message": "Your email is already confirmed"}
        background_tasks.add_task(send_email, EmailStr(user.email), user.username, str(request.base_url))
    return {"detail": "Check your email for confirmation."}
