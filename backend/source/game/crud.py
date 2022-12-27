import os
import json
import random
from sqlalchemy.ext.asyncio import AsyncSession
from game import models, schemas, errors
from users.crud import get_user_by_id


with open(os.path.join(os.path.dirname(__file__), "docker_names.json")) as f:
    docker_names = json.load(f)
    LEFT_NAMES = docker_names["left"]
    RIGHT_NAMES = docker_names["right"]


async def get_active_games(db: AsyncSession):
    active_games = await db.execute(models.Game.__table__.select().where(models.Game.is_active == True))
    active_games = active_games.all()
    return [
        schemas.BaseGame(
            host_player=game.host_id,
            max_players=game.max_players,
            is_started=game.is_started,
            is_active=game.is_active
        ) for game in active_games
    ]


async def create_game(db: AsyncSession, host_id: int, max_players: int):
    print('here', flush=True)
    left = random.choice(LEFT_NAMES)
    right = random.choice(RIGHT_NAMES)
    joining_code = f"{left}-{right}"
    game = models.Game(
        joining_code=joining_code,
        host_id=host_id,
        players=[host_id],
        max_players=max_players,
        is_started=False,
        is_active=True,
        winner=None
    )
    db.add(game)
    await db.commit()
    return schemas.JoinedGame(
        joining_code=joining_code,
        host_player=host_id,
        max_players=max_players,
        is_started=False,
        is_active=True,
        players=[await get_user_by_id(db, host_id)]
    )


async def join_game(db: AsyncSession, joining_code: str, user_id: int):
    game = await db.execute(models.Game.__table__.select().where(models.Game.joining_code == joining_code))
    game = game.first()
    if not game:
        raise errors.GameNotFound
    if game.is_started:
        raise errors.GameAlreadyStarted
    if user_id in game.players:
        raise errors.UserAlreadyInGame
    if len(game.players) >= game.max_players:
        raise errors.GameAlreadyFull
    game.players.append(user_id)
    await db.commit()
    return schemas.JoinedGame(
        joining_code=joining_code,
        host_player=game.host_id,
        max_players=game.max_players,
        is_started=game.is_started,
        is_active=game.is_active,
        players=[await get_user_by_id(db, player_id) for player_id in game.players]
    )


async def leave_game(db: AsyncSession, joining_code: str, user_id: int):
    game = await db.execute(models.Game.__table__.select().where(models.Game.joining_code == joining_code))
    game = game.first()
    if not game:
        raise errors.GameNotFound
    if user_id not in game.players:
        raise errors.UserNotInGame
    if user_id == game.host_id:
        raise errors.UserIsHost
    if game.is_started:
        raise errors.GameAlreadyStarted
    game.players.remove(user_id)
    await db.commit()
    return schemas.JoinedGame(
        joining_code=joining_code,
        host_player=game.host_id,
        max_players=game.max_players,
        is_started=game.is_started,
        is_active=game.is_active,
        players=[await get_user_by_id(db, player_id) for player_id in game.players]
    )


async def start_game(db: AsyncSession, joining_code: str, user_id: int):
    game = await db.execute(models.Game.__table__.select().where(models.Game.joining_code == joining_code))
    game = game.first()
    if not game:
        raise errors.GameNotFound
    if user_id != game.host_id:
        raise errors.UserNotHost
    if game.is_started:
        raise errors.GameAlreadyStarted
    if len(game.players) < 2:
        raise errors.NotEnoughPlayers
    game.is_started = True
    await db.commit()
    return schemas.JoinedGame(
        joining_code=joining_code,
        host_player=game.host_id,
        max_players=game.max_players,
        is_started=game.is_started,
        is_active=game.is_active,
        players=[await get_user_by_id(db, player_id) for player_id in game.players]
    )


async def end_game(db: AsyncSession, joining_code: str, user_id: int, winner: int):
    game = await db.execute(models.Game.__table__.select().where(models.Game.joining_code == joining_code))
    game = game.first()
    if not game:
        raise errors.GameNotFound
    if user_id != game.host_id:
        raise errors.UserNotHost
    if winner not in game.players:
        raise errors.UserNotInGame
    game.is_active = False
    await db.commit()
    return schemas.JoinedGame(
        joining_code=joining_code,
        host_player=game.host_id,
        max_players=game.max_players,
        is_started=game.is_started,
        is_active=game.is_active,
        players=[await get_user_by_id(db, player_id) for player_id in game.players]
    )
