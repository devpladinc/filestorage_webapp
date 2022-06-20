from email import header
from jose import JWTError, jwt
from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from .utils.db_conn import oauth
from logging import raiseExceptions
from . import schemas

# SECRET_KEY
# Algo - HS256
# Token expiration time - user login
SECRET_KEY = oauth['SECRET_KEY']
ALGORITHM = oauth['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = oauth['ACCESS_TOKEN_EXPIRE_MINUTES']

# scheme to tie up verification of token
# endpoint wherein you need to get the access token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# data -- payload
def create_access_token(data: dict):
    # create copy of data to pass / payload
    to_encode_data = data.copy()
    # create expiry datetime
    expiry = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # update payload with the expiry
    to_encode_data.update({"exp":expiry})

    # create jwt token
    encoded_token = jwt.encode(to_encode_data, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_token


def verify_access_token(token: str, credential_exception):
    
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # user_id inside the payload / decoded token
        # tested - id returns int, but since Optional on schema, probably can clean up
        id = decoded_token.get('user_id')
        

        if id == None:
            raise credential_exception
        # data out of the token
        # add id=id since we put id as Optional in the schema
        token_data = schemas.TokenData(id=id)
    except JWTError: 
        raise credential_exception
    
    return token_data

# function to get the current user; validate access token and get data from db
# dependency to check authorization
def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})

    return verify_access_token(token, credential_exception)