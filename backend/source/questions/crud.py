from sqlalchemy.ext.asyncio import AsyncSession
from  sqlalchemy.sql.expression import func
from questions import models, schemas, errors


async def get_categories(db: AsyncSession):
    results = await db.execute(models.Category.__table__.select())
    results = results.all()
    return [
        schemas.CategoryWithId(
            id=result.id, name=result.name, description=result.description
        ) for result in results
    ]


async def get_category(db: AsyncSession, category_id: int):
    result = await db.execute(models.Category.__table__.select().where(models.Category.id == category_id))
    result = result.first()
    if result is None:
        raise errors.CategoryDoesNotExist(category_id)
    return schemas.CategoryWithId(id=result.id, name=result.name, description=result.description)


async def get_category_by_name(db: AsyncSession, name: str):
    result = await db.execute(models.Category.__table__.select().where(models.Category.name == name))
    result = result.first()
    if result is None:
        raise errors.CategoryDoesNotExist(name)
    return schemas.CategoryWithId(id=result.id, name=result.name, description=result.description)


async def create_category(db: AsyncSession, category: schemas.Category):
    try:
        await get_category_by_name(db, category.name)
        raise errors.CategoryAlreadyExists(category.name)
    except errors.CategoryDoesNotExist:
        db_category = models.Category(name=category.name, description=category.description)
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        return schemas.CategoryWithId(
            id=db_category.id, name=db_category.name, description=db_category.description
        )


async def update_category(db: AsyncSession, category: schemas.Category, category_id: int):
    db_category = await get_category(db, category.id)
    db_category.name = category.name
    db_category.description = category.description
    await db.commit()
    await db.refresh(db_category)
    return schemas.CategoryWithId(
        id=db_category.id, name=db_category.name, description=db_category.description
    )


async def delete_category(db: AsyncSession, category_id: int):
    db_category = await get_category(db, category_id)
    await db.delete(db_category)
    await db.commit()


async def create_question(db: AsyncSession, question: schemas.Question):
    category = await get_category_by_name(db, question.category_name)
    category_id = category.id
    db_question = models.Question(
        question=question.question,
        category_id=category_id,
        answers=question.answers,
        correct_answer=question.correct_answer
    )
    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    return schemas.QuestionWithId(
        id=db_question.id,
        question=db_question.question,
        answers=db_question.answers,
        correct_answer=db_question.correct_answer,
        category_name=question.category_name
    )


async def get_question(db: AsyncSession, question_id: int):
    result = await db.execute(models.Question.__table__.select().where(models.Question.id == question_id))
    result = result.first()
    if result is None:
        raise errors.QuestionNotFound(question_id)
    category_name = await get_category(db, result.category_id).name
    return schemas.QuestionWithId(
        id=result.id,
        question=result.question,
        answers=result.answers,
        correct_answer=result.correct_answer,
        category_name=category_name
    )


async def update_question(db: AsyncSession, question: schemas.Question, question_id: int):
    category = await get_category_by_name(db, question.category_name)
    category_id = category.id
    db_question = await get_question(db, question_id)
    if not db_question:
        return errors.QuestionNotFound
    
    db_question.question = question.question
    db_question.category_id = category_id
    db_question.answers = question.answers
    db_question.correct_answer = question.correct_answer

    await db.commit()
    await db.refresh(db_question)
    return schemas.QuestionWithId(
        id=db_question.id,
        question=db_question.question,
        answers=db_question.answers,
        correct_answer=db_question.correct_answer,
        category_name=question.category_name
    )


async def delete_question(db: AsyncSession, question_id: int):
    db_question = await get_question(db, question_id)
    await db.delete(db_question)
    await db.commit()


async def get_random_question(db: AsyncSession, exclude_ids: list[int]=list()):
    result = await db.execute(
        models.Question.__table__.select().where(~models.Question.id.in_(exclude_ids)).order_by(func.random()).limit(1)
    )
    result = result.first()
    if result is None:
        raise errors.NoQuestionsFound()
    return schemas.QuestionWithId(
        id=result.id,
        question=result.question,
        answers=result.answers,
        correct_answer=result.correct_answer,
        category_name=get_category(db, result.category_id).name
    )


async def get_random_question_by_category(db: AsyncSession, category_name: str, exclude_ids: list[int]=list()):
    category = await get_category_by_name(db, category_name)
    category_id = category.id
    result = await db.execute(models.Question.__table__.select().where(
        ~models.Question.id.in_(exclude_ids) & (models.Question.category_id == category_id)
    ).order_by(func.random()).limit(1))
    result = result.first()

    if result is None:
        raise errors.NoQuestionsFound()

    return schemas.QuestionWithId(
        id=result.id,
        question=result.question,
        answers=result.answers,
        correct_answer=result.correct_answer,
        category_name=category_name
    )
