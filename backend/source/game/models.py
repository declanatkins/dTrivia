from sqlalchemy import Column, Integer, String, ARRAY, Boolean
from db import Base


class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    joining_code = Column(String, unique=True, index=True)
    host_id = Column(Integer)
    players = Column(ARRAY(Integer))
    max_players = Column(Integer)
    is_started = Column(Boolean)
    is_active = Column(Boolean)
    winner = Column(Integer)