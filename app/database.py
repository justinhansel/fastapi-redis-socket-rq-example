from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.settings import Settings

DB_URL = Settings.config("DB_URL")

conn_args = {}

if "sqlite" not in DB_URL:
    DB_URL = "postgresql://{}:{}@{}/{}".format(
        Settings.config("DB_USER"),
        Settings.config("DB_PASS"),
        DB_URL,
        Settings.config("DB_NAME")
    )
else:
    conn_args["check_same_thread"] = False if "sqlite" in DB_URL else True

engine = create_engine(
    DB_URL, connect_args=conn_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session_local():
    return SessionLocal()



