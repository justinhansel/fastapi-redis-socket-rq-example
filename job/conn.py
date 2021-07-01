import os

from redis import Redis

try:
    os.environ["DB_URL"]
except KeyError as e:
    os.environ["DB_URL"] = "sqlite:///sqlite.db"

from app.database import get_session_local

session = get_session_local()
redis = Redis()


def get_session_in_worker():
    return session


def get_redis_in_worker():
    return redis
