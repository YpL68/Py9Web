import pathlib

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware

from src.database.db import get_db, redis_db
from src.routes import contacts, front, auth, users

BASE_DIR = pathlib.Path(__file__).parent

app = FastAPI()


@app.on_event("startup")
async def startup():
    await FastAPILimiter.init(redis_db)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:5500', 'http://localhost:5500'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc_: ValueError):
    """
    The value_error_exception_handler function is a custom exception handler that returns a JSON response with the
    message; when it catches an exception of type ValueError.

    :param request: Request: Access the request object
    :param exc_: ValueError: Catch any value error exceptions that are raised in the app
    :return: A json response object with a status code of 400 and the exception message
    :doc-author: Trelent
    """
    return JSONResponse(
        status_code=400,
        content={"message": f"{request.url}: {str(exc_)}"}
    )


@app.exception_handler(ValidationError)
async def validation_error_exception_handler(request: Request, exc_: ValidationError):
    """
    The validation_error_exception_handler function is a custom exception handler that returns a JSON response with
    a status code of 422 and the error message. This function is used to handle ValidationError exceptions.

    :param request: Request: Access the request object, which contains information about the http request
    :param exc_: ValidationError: Catch any validation error exceptions that might occur
    :return: A json response with a 422 status code,
    :doc-author: Trelent
    """
    return JSONResponse(
        status_code=422,
        content={"message": f"{request.url}: {str(exc_)}"}
    )


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks if the database is configured correctly.
    It does this by executing a SQL query and checking if it returns any results. If it doesn't, then the
    database isn't configured correctly.

    :param db: Session: Get the database session
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if db.in_transaction():
            db.commit()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=e.detail)
    except Exception:
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(contacts.router, prefix='/api')
app.include_router(front.router)
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
