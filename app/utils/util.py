# keeping all hasing algo in one place
from passlib.context import CryptContext

# default hashing algo
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def bcrypthash(password : str):
    return pwd_context.hash(password)