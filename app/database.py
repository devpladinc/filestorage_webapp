from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from google.cloud import storage
from logging import raiseExceptions
from fastapi import status, HTTPException
from .utils.db_conn import db_creds as dbc
from .utils.db_conn import gcp_creds as gbc

# change env here
dbenv = 'local'

# SQLALCHEMY_DATABASE_URL = '<type of db>://<username>:<password>@<ip-address>/<hostname>/<database>'
SQLALCHEMY_DATABASE_URL = (f"postgresql://{dbc[dbenv]['user']}:{dbc[dbenv]['password']}@{dbc[dbenv]['host']}/{dbc[dbenv]['database']}")
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# dependency -- get a session to the database
# needs to be added as another parameter to path operations
# close session after session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def get_gcp_client():
    try:
        storage_client = storage.Client.from_service_account_json(gbc[dbenv]['service_account'])
    except ValueError as e:
        return {
            "status_code":403,
            "detail": f"{e}"
        }
    return storage_client


async def check_bucket():
    storage_client = get_gcp_client()

    bucket_count = len(list(storage_client.list_buckets()))
    # no buckets found
    if bucket_count == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No available buckets found")
    try:
        bucket = storage_client.get_bucket(gbc[dbenv]['bucket'])
    except Exception:
        return False
    return True


def upload_file(filename : str):
    storage_client = get_gcp_client()

    try:
        bucket = storage_client.bucket(gbc[dbenv]['bucket'])
        blob = bucket.blob(filename)
        blob.upload_from_filename(filename)

        # blob media link for saving to db
        return blob.media_link

    except Exception as e:
        return {
            "status_code":500,
            "detail": f"{e}"
        }

