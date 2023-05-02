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


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc_: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": f"{request.url}: {str(exc_)}"}
    )


@app.exception_handler(ValidationError)
async def validation_error_exception_handler(request: Request, exc_: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": f"{request.url}: {str(exc_)}"}
    )


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
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
