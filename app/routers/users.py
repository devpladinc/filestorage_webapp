from typing import List
from .. import models, schemas
from sqlalchemy.orm import Session
from logging import raiseExceptions
from fastapi import status, Response, Depends, APIRouter
from ..database import get_db
from ..utils import util

router = APIRouter(
    prefix = "/users"
)

@router.get("/", response_model=List[schemas.AllUsers])
async def all_users(db: Session = Depends(get_db)):
    all_user = db.query(models.Users).all()
    return all_user


@router.get("/{user_id}", response_model=schemas.AllUsers)
async def get_user(user_id : int, db: Session = Depends(get_db)):
    selected_user = db.query(models.Users).filter(models.Users.user_id==user_id).first()

    if selected_user == None:
        raiseExceptions(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with user ID {user_id} was not found")
    
    return selected_user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserCreateOut)
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


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id : int, db: Session = Depends(get_db)):
    # deletes user from db
    
    user_to_delete = db.query(models.Users).filter(models.Users.user_id==user_id)

    if user_to_delete.first() == None:
        raiseExceptions(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with user ID {user_id} was not found")

    user_to_delete.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)