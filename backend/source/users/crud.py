import hashlib
import os
from sqlalchemy.ext.asyncio import AsyncSession
from users import models, schemas, errors
from users.session import create_session


async def get_user(db: AsyncSession, user_id: int):
    result =  await db.query(models.User).filter(models.User.id == user_id).first()
    if result is None:
        raise errors.UserNotFound(user_id)
    return schemas.User(
        id=result.id,
        username=result.username,
        email=result.email,
        is_active=result.is_active
    )


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.query(models.User).filter(models.User.username == username).first()
    if result is None:
        raise errors.UserNotFound(username)
    return schemas.User(
        id=result.id,
        username=result.username,
        email=result.email,
        is_active=result.is_active
    )


async def get_user_by_email(db: AsyncSession, email: str):
    result =  await db.query(models.User).filter(models.User.email == email).first()
    if result is None:
        raise errors.UserNotFound(email)
    return schemas.User(
        id=result.id,
        username=result.username,
        email=result.email,
        is_active=result.is_active
    )


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    salt = os.urandom(32)
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256',
        user.password.encode('utf-8'),
        salt,
        100000
    )
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=str(hashed_password),
        salt=salt
    )
    await db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return schemas.User(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        games_played=db_user.games_played,
        games_won=db_user.games_won,
        is_active=db_user.is_active
    )


async def login_user_by_username(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        raise errors.UserNotFound(username)
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        user.salt,
        100000
    )
    if str(hashed_password) == user.hashed_password:
        session_id = create_session(user.id)
        user.is_active = True
        await db.commit()
        return schemas.UserWithSession(
            id=user.id,
            username=user.username,
            email=user.email,
            games_played=user.games_played,
            games_won=user.games_won,
            is_active=user.is_active,
            session_id=session_id
        )
    raise errors.IncorrectPassword()


async def login_user_by_email(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        raise errors.UserNotFound(email)
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        user.salt,
        100000
    )
    if str(hashed_password) == user.hashed_password:
        session_id = create_session(user.id)
        user.is_active = True
        await db.commit()
        return schemas.UserWithSession(
            id=user.id,
            username=user.username,
            email=user.email,
            games_played=user.games_played,
            games_won=user.games_won,
            is_active=user.is_active,
            session_id=session_id
        )
    raise errors.IncorrectPassword()
