from fastapi import APIRouter, Header
from errors import Error, UserNotLoggedIn
from auth import schemas, crud
from auth.session import validate_session


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate):
    return await crud.create_user(user)


@router.post("/login", response_model=schemas.UserWithSession or Error)
async def login_user(
        user: schemas.UserLoginByUsername or schemas.UserLoginByEmail,
):
    if isinstance(user, schemas.UserLoginByUsername):
        user_or_error = await crud.login_user(user.username, user.password)
    else:
        user_or_error = await crud.login_user(user.email, user.password)
    return user_or_error


@router.get("/{user_id}", response_model=schemas.User or Error)
async def get_user(user_id: int, session_id: str = Header()):
    if not validate_session(session_id):
        return UserNotLoggedIn()
    user_or_error = await crud.get_user(user_id)
    return user_or_error
