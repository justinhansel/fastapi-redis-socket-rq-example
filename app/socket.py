import json

import aioredis
import asyncio

from service.user_service import get_user_by_username
from sqlalchemy.orm import Session

from app.settings import Settings
from fastapi.logger import logger
from starlette.websockets import WebSocket, WebSocketDisconnect

from shared.enum import worker_channel

worker_task = None


async def setup_worker_handler(redis):
    global worker_task
    worker_task = asyncio.create_task(worker_channel_handler(redis))


# Global redis worker channel handler..
async def worker_channel_handler(r):
    (channel,) = await r.subscribe(worker_channel)
    assert isinstance(channel, aioredis.Channel)
    try:
        while True:
            message = await channel.get()
            if message:
                logger.info("Worker channel message: %s" % message.decode("utf-8"))
    except Exception as exc:
        # TODO this needs handling better
        logger.error(exc)
    global worker_task
    done, pending = await asyncio.wait(
        [worker_task], return_when=asyncio.FIRST_COMPLETED,
    )
    logger.debug(f"Done task: {done}")
    for task in pending:
        logger.debug(f"Canceling task: {task}")
        task.cancel()
    r.close()
    await r.wait_closed()


# redis websocket implementation - https://gist.github.com/timhughes/313c89a0d587a25506e204573c8017e4
async def user_redis_connector(websocket: WebSocket, redis_uri: str = Settings.config("REDIS_URL"),
                               session: Session = None, username: str = None, listen_channel: str = worker_channel):
    user_db = get_user_by_username(session, username)

    async def consumer_handler(ws: WebSocket, r, user_id=None):
        try:
            while True:
                message = await ws.receive_text()
                if message:
                    result = {
                        "user_id": user_id,
                        "message": message
                    }
                    await r.publish(listen_channel, json.dumps(result))
        except WebSocketDisconnect as exc:
            # TODO this needs handling better
            logger.error(exc)

    async def producer_handler(r, ws: WebSocket, user_id=None):
        (redis_channel,) = await r.subscribe(listen_channel)
        assert isinstance(redis_channel, aioredis.Channel)
        try:
            while True:
                message = await redis_channel.get()
                if message:
                    result = json.loads(message)
                    if "user_id" in result and result["user_id"] == user_id:
                        await ws.send_text(message.decode("utf-8"))
        except Exception as exc:
            # TODO this needs handling better
            logger.error(exc)

    redis = await aioredis.create_redis_pool(redis_uri)

    consumer_task = consumer_handler(websocket, redis, user_id=user_db.id)
    producer_task = producer_handler(redis, websocket, user_id=user_db.id)
    done, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,
    )
    logger.debug(f"Done task: {done}")
    for task in pending:
        logger.debug(f"Canceling task: {task}")
        task.cancel()
    redis.close()
    await redis.wait_closed()
