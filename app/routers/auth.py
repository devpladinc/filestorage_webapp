from typing import List
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from logging import raiseExceptions
from fastapi import status, Response, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..database import get_db
from ..utils import util


router = APIRouter(
    tags = ["Authentication"]
)


@router.post("/login")
def login(credentials : OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm only returns 2 data, username and password. 
    # email might be placed in username field
    user = db.query(models.Users).filter(models.Users.email==credentials.username).first()

    if user == None:
        raiseExceptions(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials.")
    
    password_check = util.verifypassword(credentials.password, user.password)
    if not password_check:
        raiseExceptions(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials.")
    
    # create token
    # payload NOT necessarily email/password.
    payload = {
        "user_id" : user.user_id
    }
    token = oauth2.create_access_token(data=payload)

    return {"access_token": token, "token_type" : "bearer"}