from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlitecloud://clusjlcsnk.sqlite.cloud:8860?apikey=0OfGmBouwcdis72EcBahqeXVbwvlybWr7cGtaJsMfSw"
DATABASE_NAME = "finalisthub"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

@event.listens_for(engine, "connect")
def use_database(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute(f"USE DATABASE {DATABASE_NAME}")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
