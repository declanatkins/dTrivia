from typing import List
from pydantic import BaseModel
from users.schemas import User


class CreateGame(BaseModel):
    host_player: User
    max_players: int


class BaseGame(CreateGame):
    is_started: bool
    is_active: bool


class GameWithJoiningCode(BaseGame):
    joining_code: str


class JoinedGame(BaseGame):
    joining_code: str
    players: List[User]