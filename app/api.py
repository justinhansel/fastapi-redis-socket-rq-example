import aioredis
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.websockets import WebSocket
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.settings import Settings
from app.socket import setup_worker_handler, user_redis_connector
from router.job_router import router as job_router
from router.token_router import router as token_router
from router.user_router import router as user_router
from service.populate_service import populate_example

api = FastAPI()
api.include_router(user_router)
api.include_router(token_router)
api.include_router(job_router)

worker_task = None


@api.exception_handler(AuthJWTException)
def auth_jwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@api.on_event("startup")
async def startup():
    if Settings.config("DB_INIT") is True:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    await populate_example()

    # Setup redis worker channel listener..
    redis = await aioredis.create_redis_pool(Settings.config("REDIS_URL"))
    await setup_worker_handler(redis)


@api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: Session = Depends(get_db), auth: AuthJWT = Depends()):
    auth.jwt_required(auth_from="websocket", websocket=websocket, csrf_token=websocket.cookies.get('X-CSRF-Token'))
    jwt_user = auth.get_jwt_subject()
    await websocket.accept()
    await user_redis_connector(websocket, session=session, username=jwt_user)


@api.get("/{username}")
async def read_root(username):
    return HTMLResponse("""
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
        <script>
            var ws;
            axios.post('/login', {
                "email": "test@test.com",
                "username": "{username}",
                "password": "password",
                "csrf_secret": "asecrettoeverybody"
            }).then(function(response) {
                var authToken = response.data.access_token;
                var csrfToken = response.data.csrf_token;
                document.cookie = 'access_token_cookie=' + authToken + '; path=/';
                document.cookie = 'X-CSRF-Token=' + csrfToken + '; path=/';
                console.log(response);
                console.log(document.cookie);
                ws = new WebSocket("ws://localhost:2500/ws");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
            });
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
""".replace("{username}", username))

