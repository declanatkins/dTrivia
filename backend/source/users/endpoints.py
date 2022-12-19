from fastapi import APIRouter, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from users.errors import UserNotLoggedIn
from users import schemas, crud, models
from users.session import validate_session
from db import engine, get_db


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)


@router.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_user(db, user)


@router.post("/login", response_model=schemas.UserWithSession)
async def login_user(
        user: schemas.UserLoginByUsername or schemas.UserLoginByEmail,
        db: AsyncSession = Depends(get_db)
):
    if isinstance(user, schemas.UserLoginByUsername):
        user = await crud.login_user(db, user.username, user.password)
    else:
        user = await crud.login_user(db, user.email, user.password)
    return user


@router.get("/{user_name}", response_model=schemas.User, dependencies=[Depends(validate_session)])
async def get_user(
        user_name: str,
        db: AsyncSession = Depends(get_db)
):
    return await crud.get_user_by_username(db, user_name)
