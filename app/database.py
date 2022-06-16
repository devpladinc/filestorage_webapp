from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .utils.db_conn import db_creds as dbc

# change env here
dbenv = 'local'

# SQLALCHEMY_DATABASE_URL = '<type of db>://<username>:<password>@<ip-address>/<hostname>/<database>'
SQLALCHEMY_DATABASE_URL = (f"postgresql://{dbc[dbenv]['user']}:{dbc[dbenv]['password']}@{dbc[dbenv]['host']}/{dbc[dbenv]['database']}")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# dependency -- get a session to the database
# needs to be added as another parameter to path operations 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()