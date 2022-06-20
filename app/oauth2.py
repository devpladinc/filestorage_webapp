from jose import JWTError, jwt
from datetime import datetime, timedelta
from .utils.db_conn import oauth

# SECRET_KEY
# Algo - HS256
# Token expiration time - user login

SECRET_KEY = oauth['SECRET_KEY']
ALGORITHM = oauth['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = oauth['ACCESS_TOKEN_EXPIRE_MINUTES']

# data -- payload
def create_access_token(data: dict):
    # create copy of data to pass / payload
    to_encode_data = data.copy()
    # create expiry datetime
    expiry = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # update payload with the expiry
    to_encode_data.update({"exp":expiry})

    # create jwt token
    encoded_token = jwt.encode(to_encode_data, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_token