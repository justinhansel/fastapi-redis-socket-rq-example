from fastapi.logger import logger
from sqlalchemy.orm import Session

from app.database import get_session_local
from model.user import User
from app.security import get_password_hash


async def populate_example():
    db: Session = get_session_local()
    if not db.query(User).filter(User.email == "test@test.com").first():
        logger.info("Populating example user..")
        db_user = User(email="test@test.com", username="justin", hashed_password=get_password_hash("password"))
        db_user_two = User(email="test2@test2.com", username="john", hashed_password=get_password_hash("password"))
        db.add(db_user)
        db.add(db_user_two)
        db.commit()
        db.refresh(db_user)

    logger.info("Populating example trademarks..")

