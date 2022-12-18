from fastapi import APIRouter, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth.errors import UserNotLoggedIn
from auth import schemas, crud, models
from auth.session import validate_session
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


@router.get("/{user_name}", response_model=schemas.User)
async def get_user(
        user_name: str,
        session_id: str = Header(),
        db: AsyncSession = Depends(get_db)
):
    if not validate_session(session_id):
        raise UserNotLoggedIn()
    return await crud.get_user_by_username(db, user_name)
