import os
import argparse
from logging.handlers import RotatingFileHandler

import uvicorn

from app.api import api


import logging
from fastapi.logger import logger as fastapi_logger

from app.settings import CustomFormatter, Settings

if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
    '''
    When running with gunicorn the log handlers get suppressed instead of
    passed along to the container manager. This forces the gunicorn handlers
    to be used throughout the project.
    '''

    gunicorn_logger = logging.getLogger("gunicorn")
    log_level = gunicorn_logger.level

    root_logger = logging.getLogger()
    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")

    # Use gunicorn error handlers for root, uvicorn, and fastapi loggers
    root_logger.handlers = gunicorn_error_logger.handlers
    uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
    fastapi_logger.handlers = gunicorn_error_logger.handlers

    # Pass on logging levels for root, uvicorn, and fastapi loggers
    root_logger.setLevel(log_level)
    uvicorn_access_logger.setLevel(log_level)
    fastapi_logger.setLevel(log_level)


def get_port(_port):
    try:
        return int(_port)
    except (ValueError, TypeError) as e:
        print("Invalid port argument, defaulting to port 2500..")
        return 2500


if __name__ == "__main__":
    formatter = CustomFormatter(
        "[%(asctime)s.%(msecs)03d] %(levelname)s [%(thread)d] - %(message)s", "%Y-%m-%d %H:%M:%S")
    handler = RotatingFileHandler(Settings.config("LOG_FILE"), backupCount=0)
    handler.setFormatter(formatter)
    handler.setLevel(logging.NOTSET)

    console = logging.StreamHandler()
    console.setLevel(logging.NOTSET)
    console.setFormatter(formatter)

    logging.getLogger().setLevel(logging.NOTSET)

    fastapi_logger.addHandler(handler)
    fastapi_logger.addHandler(console)

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="Specify port to run on")
    args = parser.parse_args()
    port = get_port(args.port)
    fastapi_logger.info("Starting server on port %s.." % port)

    uvicorn.run(api, host="0.0.0.0", port=port)
