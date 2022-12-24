from pydantic import BaseModel


class UserBase(BaseModel):
    user_name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserLoginByUsername(UserBase):
    password: str
    user_name: str


class UserLoginByEmail(UserBase):
    password: str
    email: str


class User(UserBase):
    id: int
    games_played: int
    games_won: int
    is_active: bool


class UserWithSession(User):
    session_id: str