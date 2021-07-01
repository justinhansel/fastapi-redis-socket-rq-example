import logging
import os
from pydantic import BaseModel


BOOL_VALUES = ["DB_INIT"]


def load_env(env_var, default=None):
    try:
        env_val = os.environ[env_var]
    except KeyError:
        env_val = ""
        if env_var in BOOL_VALUES:
            env_val = "false"
        elif default is not None:
            env_val = default

    if env_val.isnumeric():
        env_val = int(env_val)
    elif env_val.lower() == "true":
        env_val = True
    elif env_val.lower() == "false":
        env_val = False

    return env_val


class Settings:
    __conf = {
        "DB_URL": load_env('DB_URL'),
        "DB_INIT": load_env('DB_INIT', default="false"),
        "LOG_FILE": load_env('LOG_FILE', default="log.txt"),
        "REDIS_URL": load_env('REDIS_URL', default="redis://localhost:6379")
    }
    __setters = ["username", "password"]

    @staticmethod
    def config(name):
        return Settings.__conf[name]

    @staticmethod
    def set(name, value):
        if name in Settings.__setters:
            Settings.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method")


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class JWTSettings(BaseModel):
    authjwt_secret_key: str = "secret"

