from http.client import HTTPException
from typing import List
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from fastapi import status, Response, Depends, APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from ..database import get_db
from ..utils import util


router = APIRouter(
    prefix = "/users",
    tags = ["Users"]
)
# html files
templates = Jinja2Templates(directory='./app/templates')


# needs to add db/dependencies
@router.get("/dev", response_class=HTMLResponse)
async def main_page(request : Request, db: Session = Depends(get_db)):

    users = jsonable_encoder(await all_users(db))

    context = {
        'request' : request,
        'users' : users[0]
    }
    return templates.TemplateResponse("index.html", context)


@router.get("/", response_model=List[schemas.UserOut])
async def all_users(db: Session = Depends(get_db)):
    all_user = db.query(models.Users).all()
    return all_user


@router.get("/{user_id}", response_model=schemas.UserOut)
async def get_user(user_id : int, db: Session = Depends(get_db)):
    selected_user = db.query(models.Users).filter(models.Users.user_id==user_id).first()

    if selected_user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with user ID {user_id} was not found")

    return selected_user


# dependency oauth2.get_current_user -- force check access token before executing / accessing endpoint
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserCreateOut)
async def create_user(user : schemas.UserCreate, db: Session = Depends(get_db), authorized_user : int = Depends(oauth2.get_current_user)):
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


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id : int, db: Session = Depends(get_db), authorized_user : int = Depends(oauth2.get_current_user)):
    # deletes user from db
    user_to_delete = db.query(models.Users).filter(models.Users.user_id==user_id)

    if user_to_delete.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with user ID {user_id} was not found")

    user_to_delete.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


