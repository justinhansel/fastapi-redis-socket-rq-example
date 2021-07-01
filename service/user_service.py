from sqlalchemy.orm import Session
from model.user import User
from schema.user_schema import UserCreate
from shared.util import model2dict


def get_users(session: Session, ski: int = 0, limit: int = 100):
    return [model2dict(u) for u in session.query(User).all()]


def create_user(session: Session, user: UserCreate):
    hashed_password = user.password
    db_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(session: Session, email: str):
    return session.query(User).filter(User.email == email).first()


def get_user_by_username(session: Session, username: str):
    return session.query(User).filter(User.username == username).first()


