import configparser
import pathlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

file_config = pathlib.Path(__file__).parent.parent.joinpath('conf/config.ini')
config = configparser.ConfigParser()
config.read(file_config)

username = config.get('DEV_DB', 'USER')
password = config.get('DEV_DB', 'PASSWORD')
domain = config.get('DEV_DB', 'DOMAIN')
port = config.get('DEV_DB', 'PORT')
database = config.get('DEV_DB', 'DB_NAME')

URI = f"postgresql://{username}:{password}@{domain}:{port}/{database}"

engine = create_engine(URI, echo=True)
session = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# Dependency
def get_db() -> Session:
    with session() as db:
        yield db