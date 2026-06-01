from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

db_type = os.getenv("DB_TYPE", "sqlite")

if db_type == "sqlite":
    SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./finalisthub.db")
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlitecloud://clusjlcsnk.sqlite.cloud:8860/finalisthub-dev.sqlite?apikey=0OfGmBouwcdis72EcBahqeXVbwvlybWr7cGtaJsMfSw")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if db_type == "sqlite" else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

