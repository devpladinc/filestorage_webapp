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

# response model after creating user
class UserCreateOut(BaseModel):
    user_id : int
    email: EmailStr
    created_at : datetime
    # handles sql to pydantic
    class Config:
        orm_mode = True

# response model for post:all_users
class AllUsers(BaseModel):
    user_id : int
    first_name : str
    last_name : str
    email: EmailStr
    created_at : datetime
    # handles sql to pydantic
    class Config:
        orm_mode = True

# replace with OAuth2PasswordRequestForm
# class UserLogin(BaseModel):
#     email : EmailStr
#     password : str

class Token(BaseModel):
    access_token : str
    token_type : str

# validate the data inside token ()
class TokenData(BaseModel):
    # since we only include id when we are creating token, TokenData should also check for an 'id' 
    id : Optional[str] = None


# schema for file upload - output
class Files(BaseModel):
    file_id : str
    file_name : str
    created_at : datetime

# schema for file upload - output
class FileOut(BaseModel):
    file_name : str
    file_type : str