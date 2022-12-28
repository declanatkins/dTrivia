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
    await redis.set(f'sessions/{session_id}', user_id)
    await redis.expire(f'sessions/{session_id}', 3600)
    return session_id


async def get_user_id(session_id: str = Header()) -> str:
    user_id = await redis.get(session_id)
    if user_id:
        await redis.expire(f'sessions/{session_id}', 3600)
        return user_id
    raise UserNotLoggedIn()


async def delete_session(session_id: str) -> None:
    await redis.delete(f'sessions/{session_id}')


async def validate_session(session_id: str = Header()):
    if not await redis.exists(f'sessions/{session_id}'):
        raise UserNotLoggedIn()
    await redis.expire(f'sessions/{session_id}', 3600)
