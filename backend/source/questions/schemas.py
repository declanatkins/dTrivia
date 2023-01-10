from typing import List
from pydantic import BaseModel

class Question(BaseModel):
    question: str
    answers: List[str]
    correct_answer: int
    category_name: str


class Caegory(BaseModel):
    id: int
    name: str
