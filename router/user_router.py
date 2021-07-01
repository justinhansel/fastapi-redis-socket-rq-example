from typing import List

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from app.database import get_db

from schema.user_schema import UserCreate, UserSchema
from service import user_service as user_service
from app.security import get_password_hash


router = APIRouter(
    prefix='/user',
    tags=['user'],
)


@router.post("")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user_email = user_service.get_user_by_email(db, user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_username = user_service.get_user_by_username(db, user.username)
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    user.password = get_password_hash(user.password)
    return user_service.create_user(db, user=user)


@router.get("", response_model=List[UserSchema])
async def get_users(session: Session = Depends(get_db), auth: AuthJWT = Depends()):
    auth.jwt_required()
    jwt_user = auth.get_jwt_subject()
    users = user_service.get_users(session)
    return users

