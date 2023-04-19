from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.database.db import get_db
from src.routes import contacts, front, auth

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc_: ValueError):
    return JSONResponse(
        status_code=400,
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
app.include_router(auth.router)
