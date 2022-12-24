from pydantic import BaseModel


class UserBase(BaseModel):
    user_name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserLoginByUsername(BaseModel):
    password: str
    user_name: str


class UserLoginByEmail(BaseModel):
    password: str
    email: str


class User(UserBase):
    id: int
    games_played: int
    games_won: int
    is_active: bool


class UserWithSession(User):
    session_id: str