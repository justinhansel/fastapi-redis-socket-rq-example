from app.security import verify_password
from fastapi import Depends
from fastapi_csrf_protect import CsrfProtect
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from schema.user_schema import UserToken

from service import user_service
from starlette.exceptions import HTTPException


def create_token(user: UserToken, session: Session, auth: AuthJWT, csrf_protect: CsrfProtect = Depends()):
    db_user = user_service.get_user_by_username(session, user.username)
    csrf_token = csrf_protect.generate_csrf(user.csrf_secret)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Bad username or password")
    return {
        "access_token": auth.create_access_token(subject=db_user.username, user_claims={
            "csrf": csrf_token
        }),
        "csrf_token": csrf_token
    }
