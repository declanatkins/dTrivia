from typing import List
from pydantic import BaseModel

class Question(BaseModel):
    question: str
    answers: List[str]
    correct_answer: int
    category_name: str


class Category(BaseModel):
    id: int
    name: str
