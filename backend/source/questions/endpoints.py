import random
from typing import List
from fastapi import APIRouter, Depends, Query, Response
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from users.session import validate_session
from questions import schemas
from db import get_db
from game import models, errors


questions_router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(validate_session)]
)


@questions_router.get("/", response_model=schemas.Question)
async def get_question(
    game_code: str = Query(),
    category: str or None = Query(default=None),
    difficulty: str or None = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    game = await db.execute(models.Game.__table__.select().where(models.Game.joining_code == game_code))
    game = game.first()
    if not game:
        raise errors.GameNotFound(game_code)
    if not game.is_active:
        raise errors.GameAlreadyEnded(game_code)
    if not game.is_started:
        raise errors.GameNotStarted(game_code)
    
    url = 'https://opentdb.com/api.php'
    params = {
        'amount': 1,
        'type': 'multiple',
        'token': game.open_trivia_token
    }
    if category:
        params['category'] = category
    if difficulty:
        params['difficulty'] = difficulty
    response = requests.get(url, params=params)
    db_question = response.json()['results'][0]
    answers = db_question['incorrect_answers'] + [db_question['correct_answer']]
    answers = random.shuffle(answers)
    question = schemas.Question(
        question=db_question['question'],
        answers=answers,
        correct_answer=answers.index(db_question['correct_answer']),
        category_name=db_question['category']
    )
    return question


@questions_router.get("/categories", response_model=List[schemas.Category])
def get_categories():
    category_url = 'https://opentdb.com/api_category.php'
    response = requests.get(category_url)
    return response.json()['trivia_categories']
