from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from users.session import validate_session, get_user_id
from db import engine, get_db
from game import crud, schemas, models




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


@router.get("/", response_model=schemas.BaseGame)
async def get_active_games():
    return await crud.get_active_games()


@router.post("/", response_model=schemas.JoinedGame, status_code=status.HTTP_201_CREATED)
async def create_game(game: schemas.CreateGame, db: AsyncSession=Depends(get_db)):
    return await crud.create_game(db, game.host_player, game.max_players)


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
async def end_game(joining_code: str, user_id: int=Depends(get_user_id), db: AsyncSession=Depends(get_db)):
    return await crud.end_game(db, joining_code, user_id)