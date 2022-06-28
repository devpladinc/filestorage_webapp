from logging import raiseExceptions
from fastapi import FastAPI, Path, status, HTTPException, Response, Depends
import psycopg2 as ps
from psycopg2.extras import RealDictCursor
from typing import List
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from .utils.db_conn import db_creds
from .routers import users, auth, files

# change db env here
db_env = 'local'

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# postgres db connection
try:
    conn = ps.connect(host=db_creds[db_env]['host'],\
        database=db_creds[db_env]['database'], user=db_creds[db_env]['user'],\
        password=db_creds[db_env]['password'], cursor_factory=RealDictCursor)
    cursor = conn.cursor()
except Exception as e:
    print("Error: ", e)
   


# call routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(files.router)