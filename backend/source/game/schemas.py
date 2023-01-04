from typing import List
from pydantic import BaseModel
from users.schemas import User


class CreateGame(BaseModel):
    host_player: int
    max_players: int


class BaseGame(CreateGame):
    is_started: bool
    is_active: bool


class JoinedGame(BaseGame):
    joining_code: str
    players: List[User]


class Game(BaseGame):
    player_count: int
    host_player_object: User


class GameEnd(BaseModel):
    winner: int