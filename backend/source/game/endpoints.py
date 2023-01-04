from typing import List
from aioredis import Redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from users.session import validate_session, get_user_id
from db import engine, get_db
from game import crud, schemas, models, errors
from settings import get_settings


settings = get_settings()


router = APIRouter(
    prefix="/games",
    tags=["Game"],
    dependencies=[Depends(validate_session)],
    responses={404: {"description": "Not found"}},
)


@router.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    
    # See what games are in the DB and not in redis
    # If they're not in redis, mark them as inactive
    # If they're in redis, mark them as active

    
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB
    )

    async with engine.begin() as db:
        active_games = await db.execute(models.Game.__table__.select().where(models.Game.is_active == True))
        active_games = active_games.all()
        games_in_redis = await redis.keys("games/*")
        for game in active_games:
            if game.joining_code not in games_in_redis:
                await db.execute(models.Game.__table__.update().where(models.Game.id == game.id).values(is_active=False))


@router.get("/", response_model=List[schemas.Game])
async def get_active_games(db: AsyncSession=Depends(get_db)):
    return await crud.get_active_games(db)


@router.post("/", response_model=schemas.JoinedGame, status_code=status.HTTP_201_CREATED)
async def create_game(game: schemas.CreateGame, db: AsyncSession=Depends(get_db)):
    return await crud.create_game(db, game.host_player, game.max_players)


@router.get("/{joining_code}", response_model=schemas.JoinedGame)
async def get_game(joining_code: str, user_id: int=Depends(get_user_id), db: AsyncSession=Depends(get_db)):
    try:
        return await crud.join_game(db, joining_code, user_id)
    except (errors.UserAlreadyInGame, errors.GameAlreadyStarted):
        return await crud.get_game(db, joining_code)


@router.post("/{joining_code}/join", response_model=schemas.JoinedGame)
async def join_game(joining_code: str, user_id: int=Depends(get_user_id), db: AsyncSession=Depends(get_db)):
    return await crud.join_game(db, joining_code, user_id)


@router.post("/{joining_code}/start", response_model=schemas.JoinedGame)
async def start_game(joining_code: str, user_id: int=Depends(get_user_id), db: AsyncSession=Depends(get_db)):
    return await crud.start_game(db, joining_code, user_id)


@router.post("/{joining_code}/leave", response_model=schemas.JoinedGame)
async def leave_game(joining_code: str, user_id: int=Depends(get_user_id), db: AsyncSession=Depends(get_db)):
    return await crud.leave_game(db, joining_code, user_id)


@router.post("/{joining_code}/end", response_model=schemas.JoinedGame)
async def end_game(joining_code: str, results: schemas.GameEnd, user_id: int=Depends(get_user_id), db: AsyncSession=Depends(get_db)):
    return await crud.end_game(db, joining_code, user_id, results.winner)