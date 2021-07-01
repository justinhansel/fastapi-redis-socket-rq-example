from fastapi import Depends, APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app.database import get_db
from service import job_service as job_service

router = APIRouter(
    prefix='/job',
    tags=['job'],
)


@router.post("/basic")
async def job_basic(session: Session = Depends(get_db), auth: AuthJWT = Depends()):
    auth.jwt_required()
    jwt_user = auth.get_jwt_subject()

    return {
        "job_id": job_service.basic_job_start(session, jwt_user)
    }


@router.post("/basic_arg")
async def job_basic_arg(session: Session = Depends(get_db), auth: AuthJWT = Depends()):
    auth.jwt_required()
    jwt_user = auth.get_jwt_subject()
    return {
        "job_id": job_service.basic_job_arg_start(2, session, jwt_user)
    }


@router.post("/database")
async def job_db(session: Session = Depends(get_db), auth: AuthJWT = Depends()):
    auth.jwt_required()
    jwt_user = auth.get_jwt_subject()

    return {
        "job_id": job_service.database_job_start(session, jwt_user)
    }


@router.get("/fetch/{job_id}")
async def fetch_job(job_id, session: Session = Depends(get_db), auth: AuthJWT = Depends()):
    # Job information only available for 500 seconds default
    return job_service.fetch_job(job_id)

