from sqlalchemy import Column, Integer, String, ARRAY
from db import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    answers = Column(ARRAY(String))
    correct_answer = Column(Integer)
    category_id = Column(Integer)
