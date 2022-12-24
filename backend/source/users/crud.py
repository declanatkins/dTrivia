import hashlib
import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from users import models, schemas, errors
from users.session import create_session


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(models.User.__table__.select().where(models.User.id == user_id))
    result = result.first()
    if result is None:
        raise errors.UserNotFound(user_id)
    return schemas.User(
        id=result.id,
        user_name=result.user_name,
        email=result.email,
        is_active=result.is_active
    )


async def get_user_by_user_name(db: AsyncSession, user_name: str):
    result = await db.execute(models.User.__table__.select().where(models.User.user_name == user_name))
    result = result.first()
    if result is None:
        raise errors.UserDoesNotExist(user_name)
    return schemas.User(
        id=result.id,
        user_name=result.user_name,
        email=result.email,
        is_active=result.is_active,
        games_played=result.games_played,
        games_won=result.games_won
    )


async def get_user_by_email(db: AsyncSession, email: str):
    result =  await db.execute(models.User.__table__.select().where(models.User.email == email))
    result = result.first()
    if result is None:
        raise errors.UserDoesNotExist(email)
    return schemas.User(
        id=result.id,
        user_name=result.user_name,
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
        user_name=user.user_name,
        email=user.email,
        hashed_password=hashed_password,
        salt=salt
    )

    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError as e:
        if 'email' in str(e):
            raise errors.UserAlreadyExists(user.email)
        else:
            raise errors.UserAlreadyExists(user.user_name)
    return schemas.User(
        id=db_user.id,
        user_name=db_user.user_name,
        email=db_user.email,
        games_played=db_user.games_played,
        games_won=db_user.games_won,
        is_active=db_user.is_active
    )


async def login_user_by_user_name(db: AsyncSession, user_name: str, password: str):
    user = await get_user_by_user_name(db, user_name)
    if not user:
        raise errors.UserNotFound(user_name)
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        user.salt,
        100000
    )
    if hashed_password == user.hashed_password:
        session_id = create_session(user.id)
        user.is_active = True
        await db.commit()
        return schemas.UserWithSession(
            id=user.id,
            user_name=user.user_name,
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
    if hashed_password == user.hashed_password:
        session_id = create_session(user.id)
        user.is_active = True
        await db.commit()
        return schemas.UserWithSession(
            id=user.id,
            user_name=user.user_name,
            email=user.email,
            games_played=user.games_played,
            games_won=user.games_won,
            is_active=user.is_active,
            session_id=session_id
        )
    raise errors.IncorrectPassword()
