from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

test_mode = os.getenv("TEST", "false").lower() == "true"

if test_mode:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./finalisthub_test.db"
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlitecloud://clusjlcsnk.sqlite.cloud:8860/finalisthub-dev.sqlite?apikey=0OfGmBouwcdis72EcBahqeXVbwvlybWr7cGtaJsMfSw")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if test_mode else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


