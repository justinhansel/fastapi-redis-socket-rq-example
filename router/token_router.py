from fastapi import Depends, APIRouter
from fastapi_csrf_protect import CsrfProtect
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app.database import get_db
from app.settings import JWTSettings
from schema.user_schema import UserToken
from service.token_service import create_token

router = APIRouter(
    tags=['token'],
)


@AuthJWT.load_config
def get_config():
    return JWTSettings()


@router.post('/login')
async def login(user: UserToken, session: Session = Depends(get_db), auth: AuthJWT = Depends(),
                csrf_protect: CsrfProtect = Depends()):
    return create_token(user, session, auth, csrf_protect)
