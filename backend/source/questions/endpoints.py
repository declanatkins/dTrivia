from typing import List
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from questions import schemas, crud, models
from db import engine, get_db


categories_router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    responses={404: {"description": "Not found"}},
)

questions_router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
    responses={404: {"description": "Not found"}},
)


@questions_router.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@categories_router.get("/", response_model=list[schemas.CategoryWithId])
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await crud.get_categories(db)


@categories_router.get("/{category_name}", response_model=schemas.CategoryWithId)
async def get_category(category_name: str, db: AsyncSession = Depends(get_db)):
    return await crud.get_category_by_name(db, category_name)


@categories_router.post("/", response_model=schemas.CategoryWithId)
async def create_category(category: schemas.Category, db: AsyncSession = Depends(get_db)):
    return await crud.create_category(db, category)


@categories_router.put("/{category_id}", response_model=schemas.CategoryWithId)
async def update_category(category: schemas.Category, category_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.update_category(db, category, category_id)


@categories_router.delete("/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_category(db, category_id)
    return Response(status_code=204)


@categories_router.get("/{category_name}/random", response_model=schemas.QuestionWithId)
async def get_random_question_by_category(
        category_name: str,
        db: AsyncSession = Depends(get_db),
        exclude_ids: List[int] = Query(list())
):
    return await crud.get_random_question_by_category(db, category_name, exclude_ids)


@questions_router.get("/{question_id}", response_model=schemas.QuestionWithId)
async def get_question(question_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_question(db, question_id)


@questions_router.post("/", response_model=schemas.QuestionWithId)
async def create_question(question: schemas.Question, db: AsyncSession = Depends(get_db)):
    return await crud.create_question(db, question)


@questions_router.put("/{question_id}", response_model=schemas.QuestionWithId)
async def update_question(question: schemas.Question, question_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.update_question(db, question, question_id)


@questions_router.delete("/{question_id}")
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_question(db, question_id)
    return Response(status_code=204)


@questions_router.get("/random", response_model=schemas.QuestionWithId)
async def get_random_question(
        db: AsyncSession = Depends(get_db),
        exclude_ids: List[int] = Query(list())
):
    return await crud.get_random_question(db, exclude_ids)


questions_router.include_router(categories_router)
