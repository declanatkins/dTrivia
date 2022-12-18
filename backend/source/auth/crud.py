import hashlib
import os
from sqlalchemy.ext.asyncio import AsyncSession
import errors
from auth import models, schemas


async def get_user(db: AsyncSession, user_id: int):
    return await db.query(models.User).filter(models.User.id == user_id).first()


async def get_user_by_username(db: AsyncSession, username: str):
    return await db.query(models.User).filter(models.User.username == username).first()


async def get_user_by_email(db: AsyncSession, email: str):
    return await db.query(models.User).filter(models.User.email == email).first()


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
    return db_user


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
        return user
    return errors.IncorrectPassword


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
        return user
    raise errors.IncorrectPassword()