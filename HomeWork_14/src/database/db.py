from fastapi import HTTPException, status
import redis.asyncio as redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import exc

from src.conf.config import settings

URI = settings.uri

engine = create_engine(URI, echo=True)
session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

redis_db = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)


# Dependency
def get_db() -> Session:
    with session() as db:
        try:
            yield db
        except exc.SQLAlchemyError as err:
            if db.in_transaction():
                db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
