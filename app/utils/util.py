# keeping all hasing algo in one place
from passlib.context import CryptContext

# default hashing algo
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def bcrypthash(password : str):
    return pwd_context.hash(password)

# .verify from CryptContext
# verify handles the conversation and comparing of plain and hashed password
def verifypassword(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
    