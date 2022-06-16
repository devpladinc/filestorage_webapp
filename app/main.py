from fastapi import FastAPI, Path, status, HTTPException, Response, Depends
import psycopg2 as ps
from psycopg2.extras import RealDictCursor
from typing import Optional, List
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db
from .utils.db_conn import db_creds
from .utils import util

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
   

@app.get("/")
async def root():
    return {"message": "file storage web app - health check"}


@app.post("/create-user", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user : schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # create hash for password
        hashed_password = util.bcrypthash(user.password)
        user.password = hashed_password
        
        # send all data to db
        new_user = models.Users(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    except Exception:
        return {"status":"Unable to create user "}