from typing import List
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserToken(UserCreate):
    csrf_secret: str


class UserSchema(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode: True

