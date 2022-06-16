from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# user schema
class UserCreate(BaseModel):
    first_name : str
    middle_name : str
    last_name : str
    email : EmailStr
    password : str

class UserOut(BaseModel):
    user_id : int
    email: EmailStr
    created_at : datetime
    # handles sql to pydantic
    class Config:
        orm_mode = True