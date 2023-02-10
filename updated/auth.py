from passlib.context import CryptContext


# we telling passlib what is the default hassing algorithm here it is  bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
