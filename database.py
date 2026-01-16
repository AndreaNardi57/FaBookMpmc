from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL

from typing import Annotated
## from config import get_settings

PG_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username="pescatorello",
    password="acubens@1",
    host="localhost",
    database="mpmcbiblio"
    )


# Create SQLAlchemy engine
## engine = create_engine(PG_DATABASE_URL)

engine = create_engine("postgresql+psycopg2://innktnbgftlllfaggzow:urpxujxabqmbtmpkprbkvrtaqvkjss@9qasp5v56q8ckkf5dc.leapcellpool.com:6438/zekjptozpulnobhzqrlu?sslmode=require")

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
