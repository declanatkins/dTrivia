import json
import redis
from settings import get_settings


settings = get_settings()


class Game:

    @staticmethod
    def get_games_from_redis():
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB
        )
        game_keys = r.keys('games/*')
        games = []
        for game_key in game_keys:
            games.append(Game.from_json(r.get(game_key)))
        return games
    
    @staticmethod
    def get_game_from_redis(joining_code):
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB
        )
        game_key = f'games/{joining_code}'
        if r.exists(game_key):
            return Game.from_json(r.get(game_key))
        raise KeyError(f'Game with joining code {joining_code} does not exist')
    
    def __init__(self, joining_code, max_players, host_player):
        self.joining_code = joining_code
        self.max_players = max_players
        self.host_player = host_player
        self.players = [host_player]
        self.used_questions = []
        self.current_question = None
        self.current_question_answers = []
        self.current_question_correct_answer = None
        self.current_scores = {}
        self.current_question_start_time = None
        self.is_started = False
        self.is_finished = False
    
    def add_player(self, player):
        self.players.append(player)
    
    def remove_player(self, player):
        self.players.remove(player)
    
    def commit_to_redis(self):
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB
        )
        r.set(f'games/{self.joining_code}', json.dumps(self.to_json()))
    
    def to_json(self):
        return {
            'joining_code': self.joining_code,
            'max_players': self.max_players,
            'host_player': self.host_player,
            'players': self.players,
            'used_questions': self.used_questions,
            'current_question': self.current_question,
            'current_question_answers': self.current_question_answers,
            'current_question_correct_answer': self.current_question_correct_answer,
            'current_scores': self.current_scores,
            'current_question_start_time': self.current_question_start_time,
            'is_started': self.is_started,
            'is_finished': self.is_finished
        }
    
    @classmethod
    def from_json(cls, json_string):
        json_data = json.loads(json_string)
        base = cls(
            json_data['joining_code'],
            json_data['max_players'],
            json_data['host_player']
        )
        base.players = json_data['players']
        base.used_questions = json_data['used_questions']
        base.current_question = json_data['current_question']
        base.current_question_answers = json_data['current_question_answers']
        base.current_question_correct_answer = json_data['current_question_correct_answer']
        base.current_scores = json_data['current_scores']
        base.current_question_start_time = json_data['current_question_start_time']
        base.is_started = json_data['is_started']
        base.is_finished = json_data['is_finished']
        return base
