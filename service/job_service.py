from time import sleep

from redis import Redis
from rq import Queue

from fastapi.logger import logger
from service.user_service import get_user_by_username
from sqlalchemy.orm import Session

from job.job import basic_job, basic_job_arg, database_job

job_queue = Queue(connection=Redis(), name="job_queue")


def basic_job_start(session: Session, username):
    try:
        user_db = get_user_by_username(session, username)
        job = job_queue.enqueue(basic_job, user_db.id)
    except Exception as e:
        logger.error('An error occurred while trying to create basic job.')
        raise e
    return job.id


def basic_job_arg_start(duration, session: Session, username):
    try:
        user_db = get_user_by_username(session, username)
        job = job_queue.enqueue(basic_job_arg, duration, user_db.id)
    except Exception as e:
        logger.error('An error occurred while trying to create basic arg job.')
        raise e
    return job.id


def database_job_start(session: Session, username):
    try:
        user_db = get_user_by_username(session, username)
        job = job_queue.enqueue(database_job, user_db.id)
    except Exception as e:
        logger.error('An error occurred while trying to create database job.')
        raise e
    return job.id


def fetch_job(task_id):
    logger.info('Fetching job with id: %s' % task_id)
    job = job_queue.fetch_job(task_id)
    if job is None:
        return {
            "id": -1,
            "found": False
        }
    return {
        "id": job.id,
        "found": True,
        "result": job.result,
        "is_failed": job.is_failed,
        "is_finished": job.is_finished,
        "is_queued": job.is_queued,
        "is_started": job.is_started,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "ended_at": job.ended_at
    }
