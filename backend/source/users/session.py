import os
from aioredis import Redis
from fastapi import Header
from users.errors import UserNotLoggedIn
from settings import get_settings


settings = get_settings()
redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB
)


async def create_session(user_id: str) -> str:
    session_id = await redis.get(user_id)
    if session_id:
        return session_id
    session_id = os.urandom(32).hex()
    await redis.set(user_id, session_id)
    await redis.expire(user_id, 3600)
    return session_id


async def get_user_id(session_id: str) -> str:
    user_id = await redis.get(session_id)
    if user_id:
        await redis.expire(session_id, 3600)
        return user_id
    raise UserNotLoggedIn()


async def delete_session(session_id: str) -> None:
    await redis.delete(session_id)


async def delete_user_sessions(user_id: str) -> None:
    await redis.delete(user_id)


async def validate_session(session_id: str = Header()):
    if not await redis.exists(session_id):
        raise UserNotLoggedIn()
