from aioredis import Redis
from fastapi import APIRouter, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from users import schemas, crud, models
from users.session import validate_session, delete_session
from db import engine, get_db
from settings import get_settings


settings = get_settings()


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)


@router.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB
    )
    for key in await redis.keys("sessions/*"):
        await redis.delete(key)

    async with engine.begin() as db:
        active_users = await db.execute(models.User.__table__.select().where(models.User.is_active == True))
        active_users = active_users.all()
        for user in active_users:
            await db.execute(models.User.__table__.update().where(models.User.id == user.id).values(is_active=False))


@router.post("/", response_model=schemas.User, status_code=201)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_user(db, user)


@router.post("/login", response_model=schemas.UserWithSession)
async def login_user(
        user: schemas.UserLoginByUsername | schemas.UserLoginByEmail,
        db: AsyncSession = Depends(get_db)
):
    if isinstance(user, schemas.UserLoginByUsername):
        user = await crud.login_user_by_user_name(db, user.user_name, user.password)
    else:
        user = await crud.login_user_by_email(db, user.email, user.password)
    return user


@router.post("/logout", dependencies=[Depends(validate_session)])
async def logout_user(session_id: str = Header(alias="session-id")):
    delete_session(session_id)


@router.get("/{user_name}", response_model=schemas.User, dependencies=[Depends(validate_session)])
async def get_user(
        user_name: str,
        db: AsyncSession = Depends(get_db)
):
    return await crud.get_user_by_user_name(db, user_name)
