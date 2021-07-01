from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


class CsrfSettings(BaseModel):
    secret_key: str = 'asecrettoeverybody'


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()
