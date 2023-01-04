import json
import redis
from settings import get_settings
from utils import make_backend_request


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
    
    @staticmethod
    def delete_game_from_redis(joining_code):
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB
        )
        game_key = f'games/{joining_code}'
        if r.exists(game_key):
            r.delete(game_key)
            return
        raise KeyError(f'Game with joining code {joining_code} does not exist')

    def __init__(self, joining_code, max_players, host_player, question_count, exclude_categories=list()):
        self.joining_code = joining_code
        self.max_players = max_players
        self.host_player = host_player
        self.players = [host_player]
        self.in_game_players = []
        self.used_questions = []
        self.current_question = None
        self.current_scores = {host_player: 0}
        self.is_started = False
        self.is_finished = False
        self.total_questions = question_count
        self.exclude_categories = exclude_categories

    def next_question(self):
        if self.current_question is not None:
            self.used_questions.append(self.current_question)
        if len(self.used_questions) >= int(self.total_questions):
            self.is_finished = True
            raise ValueError('Game is finished')
        
        params = {}
        if self.used_questions:
            params['exclude_ids'] = [q['id'] for q in self.used_questions]

        if self.exclude_categories:
            params['exclude_categories'] = self.exclude_categories
        params = params or None

        response = make_backend_request('get', 'questions/actions/random', params=params)
        if response.status_code == 200:
            self.current_question = response.json()
    
    def add_player(self, player):
        self.players.append(player)
        self.current_scores[player] = 0

    def add_in_game_player(self, player):
        self.in_game_players.append(player)
    
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
        r.expire(f'games/{self.joining_code}', 3600)
    
    def to_json(self):
        return {
            'joining_code': self.joining_code,
            'max_players': self.max_players,
            'host_player': self.host_player,
            'players': self.players,
            'used_questions': self.used_questions,
            'current_question': self.current_question,
            'current_scores': self.current_scores,
            'is_started': self.is_started,
            'is_finished': self.is_finished,
            'in_game_players': self.in_game_players,
            'total_questions': self.total_questions,
            'exclude_categories': self.exclude_categories
        }
    
    @classmethod
    def from_json(cls, json_string):
        json_data = json.loads(json_string)
        base = cls(
            json_data['joining_code'],
            json_data['max_players'],
            json_data['host_player'],
            json_data['total_questions'],
            json_data['exclude_categories']
        )
        base.players = json_data['players']
        base.used_questions = json_data['used_questions']
        base.current_question = json_data['current_question']
        base.current_scores = json_data['current_scores']
        base.is_started = json_data['is_started']
        base.is_finished = json_data['is_finished']
        base.in_game_players = json_data['in_game_players']
        return base
