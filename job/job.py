import json
from random import randrange
from time import sleep

from rq import get_current_job
from sqlalchemy.orm import Session

from job.conn import get_session_in_worker, get_redis_in_worker
from model.user import User
from shared.enum import JobType, JobStatus, worker_channel
from shared.util import model2dict


def basic_job(user_id):
    with get_redis_in_worker() as redis:
        job = get_current_job()
        job_id = job.id
        redis.publish(worker_channel, json.dumps({
            "job_type": JobType.BASIC.name,
            "status": JobStatus.STARTED.name,
            "job_id": job_id,
            "user_id": user_id
        }))

        # Actual job logic here..
        print("Doing basic job..")
        sleep(randrange(1, 3))
        print("Completed basic job.")

        result = {
            "job_type": JobType.BASIC.name,
            "status": JobStatus.COMPLETE.name,
            "job_id": job_id,
            "user_id": user_id
        }
        redis.publish(worker_channel, json.dumps(result))
        return result


def basic_job_arg(time, user_id):
    with get_redis_in_worker() as redis:
        job = get_current_job()
        job_id = job.id
        redis.publish(worker_channel, json.dumps({
            "job_type": JobType.BASIC_ARG.name,
            "status": JobStatus.STARTED.name,
            "job_id": job_id,
            "user_id": user_id
        }))

        print("Doing job with arg..")
        sleep(time)
        print("Completed job with arg.")

        result = {
            "job_type": JobType.BASIC_ARG.name,
            "status": JobStatus.COMPLETE.name,
            "job_id": job_id,
            "user_id": user_id
        }

        redis.publish(worker_channel, json.dumps(result))
        return result


def database_job(user_id):
    with get_session_in_worker() as session:
        with get_redis_in_worker() as redis:
            job = get_current_job()
            job_id = job.id
            redis.publish(worker_channel, json.dumps({
                "job_type": JobType.DATABASE.name,
                "status": JobStatus.STARTED.name,
                "job_id": job_id,
                "user_id": user_id
            }))

            print("Doing database job..")
            db: Session = session
            db_result = [model2dict(u) for u in db.query(User).all()]

            result = {
                "job_type": JobType.DATABASE.name,
                "status": JobStatus.COMPLETE.name,
                "job_id": job_id,
                "result": db_result,
                "user_id": user_id
            }
            print("Completed database job: %s " % result)
            redis.publish(worker_channel, json.dumps(result))
            return result
