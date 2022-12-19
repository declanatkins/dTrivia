from sqlalchemy import Boolean, Column, Integer, String
from db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    salt = Column(String)
    is_active = Column(Boolean, default=True)
    games_played = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
