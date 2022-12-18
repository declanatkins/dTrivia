from typing import List
from pydantic import BaseModel


class Category(BaseModel):
    name: str
    description: str


class CategoryWithId(Category):
    id: int


class Question(BaseModel):
    question: str
    answers: List[str]
    correct_answer: int
    category_name: str


class QuestionWithId(Question):
    id: int
