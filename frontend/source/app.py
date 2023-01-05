import re
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)
from flask_socketio import SocketIO, emit, join_room, leave_room, emit
from settings import get_settings
from utils import login_required, make_backend_request
from threading import Lock
from game import Game


EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
game_access_lock = Lock()


app = Flask(__name__)
settings = get_settings()
app.secret_key = settings.FLASK_SECRET_KEY
socket_app = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.form.to_dict()

    # Check if an email was passed as user_name
    if re.fullmatch(EMAIL_REGEX, data['user_name']):
        data['email'] = data['user_name']
        del data['user_name']
    response = make_backend_request('post', 'users/login', data, auth=False)
    if response.status_code == 200:
        session['session_id'] = response.json()['session_id']
        session['user_name'] = response.json()['user_name']
        session['user_id'] = response.json()['id']
    else:
        flash('Invalid Credentials')
    return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    make_backend_request('post', 'users/logout')
    session.pop('session_id')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    data = request.form.to_dict()
    response = make_backend_request('post', 'users/', data, auth=False)
    if response.status_code == 201:
        flash('User created successfully')
    else:
        flash(f'Failed to create user: {response.json()["detail"]}')
    return redirect(url_for('index'))


@app.route('/create-game', methods=['GET'])
@login_required
def create_game_page():
    available_categories = make_backend_request('get', 'questions/categories/').json()
    return render_template('create_game.html', categories=available_categories)


@app.route('/create-game', methods=['POST'])
@login_required
def create_game():
    data = request.form.to_dict()
    data['host_player'] = session['user_id']
    response = make_backend_request('post', 'games/', data)
    exclude_categories = request.form.getlist('excluded_categories')
    if response.status_code == 201:
        flash('Game created successfully')
        # Create the game object
        game = Game(
            response.json()['joining_code'],
            data['max_players'],
            session['user_id'],
            data['number_of_questions'],
            exclude_categories
        )
        with game_access_lock:
            game.commit_to_redis()
        return redirect(url_for('game_lobby', joining_code=response.json()['joining_code']))
    flash(f'Failed to create game: {response.json()["detail"]}')
    return redirect(url_for('index'))


@app.route('/join-game', methods=['GET'])
@login_required
def join_game_page():
    return render_template('join_game.html')


@app.route('/join-game', methods=['POST'])
@login_required
def join_game():
    data = request.form.to_dict()
    data['joining_code'] = data['joining_code'].lower()
    response = make_backend_request('post', f'games/{data["joining_code"]}/join')
    if response.status_code == 200:

        # Update the game object
        with game_access_lock:
            game = Game.get_game_from_redis(data['joining_code'])
            game.add_player(session['user_id'])
            game.commit_to_redis()

        flash('Game joined successfully')
        return redirect(url_for('game_lobby', joining_code=response.json()['joining_code']))
    elif response.json()["detail"] == 'User already in game':
        flash('You are already in this game')
        return redirect(url_for('game_lobby', joining_code=data['joining_code']))
    flash(f'Failed to join game: {response.json()["detail"]}')
    return redirect(url_for('index'))


@app.route('/game/<joining_code>/lobby', methods=['GET'])
@login_required
def game_lobby(joining_code):
    try:
        with game_access_lock:
            game = Game.get_game_from_redis(joining_code)
        backend_game = make_backend_request('get', f'games/{joining_code}').json()
        game_players = [
            player['user_name'] for player in backend_game['players']
        ]
        game_host_id = backend_game['host_player']
    except KeyError as e:
        flash('Game not found')
        return redirect(url_for('index'))
    return render_template('game_lobby.html', game=game, game_players=game_players, game_host_id=game_host_id)


@app.route('/game/<joining_code>/game-room', methods=['GET'])
@login_required
def game_room(joining_code):
    try:
        with game_access_lock:
            game = Game.get_game_from_redis(joining_code)
        backend_game = make_backend_request('get', f'games/{joining_code}').json()
        print(backend_game)
        game_players = [
            player['user_name'] for player in backend_game['players']
        ]
        game_host_id = backend_game['host_player']
        if not backend_game['is_started']:
            flash('Game has not started yet')
            return redirect(url_for('game_lobby', joining_code=joining_code))
    except KeyError as e:
        print(e)
        flash('Game not found')
        return redirect(url_for('index'))
    return render_template('game.html', game=game, game_players=game_players, game_host_id=game_host_id)


@app.route('/game/<joining_code>/results', methods=['GET'])
@login_required
def game_results(joining_code):
    try:
        with game_access_lock:
            game = Game.get_game_from_redis(joining_code)
        backend_game = make_backend_request('get', f'games/{joining_code}').json()
        user_id_to_name = {
            player['id']: player['user_name'] for player in backend_game['players']
        }
        if not game.is_finished:
            flash('Game has not finished yet')
            return redirect(url_for('game_lobby', joining_code=joining_code))
        
        sorted_scores = sorted(game.current_scores.items(), key=lambda x: x[1], reverse=True)
        scores_with_user_names = {
            user_id_to_name[int(user_id)]: score for user_id, score in sorted_scores
        }
        make_backend_request('post', f'games/{joining_code}/end', data={'winner': int(sorted_scores[0][0])})
        return render_template('results.html', game=game, scores=scores_with_user_names)
    except KeyError as e:
        print('end', e)
        flash('Game not found')
        return redirect(url_for('index'))


@socket_app.on('lobby/join')
def lobby_on_join(data):
    join_room(data['joining_code'])
    backend_game = make_backend_request('get', f'games/{data["joining_code"]}').json()
    game_players = [
        player['user_name'] for player in backend_game['players']
    ]
    emit('lobby/player-joined', {'players': game_players}, to=data['joining_code'])


@socket_app.on('lobby/leave')
def lobby_on_leave(data):
    leave_room(data['joining_code'])
    with game_access_lock:
        game = Game.get_game_from_redis(data['joining_code'])
        game.remove_player(session['user_id'])
        game.commit_to_redis()
    emit('lobby/player-left', {}, to=data['joining_code'])


@socket_app.on('lobby/start-game')
def lobby_on_start_game(data):
    response = make_backend_request('post', f'games/{data["joining_code"]}/start')
    if response.status_code == 200:
        flash('Game started successfully')
        with game_access_lock:
            game = Game.get_game_from_redis(data['joining_code'])
            game.is_started = True
            game.commit_to_redis()
        emit('lobby/game-started', {}, to=data['joining_code'])
    flash(f'Failed to start game: {response.json()["detail"]}')


@socket_app.on('lobby/cancel-game')
def lobby_on_cancel_game(data):
    response = make_backend_request('post', f'games/{data["joining_code"]}/cancel')
    if response.status_code == 200:
        flash('Game cancelled successfully')
        with game_access_lock:
            Game.delete_game_from_redis(data['joining_code'])
        emit('lobby/game-cancelled', {}, to=data['joining_code'])
    flash(f'Failed to cancel game: {response.json()["detail"]}')


@socket_app.on('game/join')
def game_on_join(data):
    join_room(data['joining_code'])
    emit('game/player-joined', to=data['joining_code'])

    with game_access_lock:
        game = Game.get_game_from_redis(data['joining_code'])
        game.add_in_game_player(session['user_id'])
        game.commit_to_redis()
        if len(game.in_game_players) == len(game.players):
            emit('game/start', to=data['joining_code'])


@socket_app.on('game/next-question')
def game_on_next_question(data):
    room = data['joining_code']

    try:
        with game_access_lock:
            game = Game.get_game_from_redis(room)
            game.next_question()
            game.commit_to_redis()

            question = game.current_question['question']
            answers = game.current_question['answers']

            emit('game/question', {'question': question, 'answers': answers}, to=room)
    except ValueError:
        with game_access_lock:
            game = Game.get_game_from_redis(room)
            game.is_finished = True
            game.commit_to_redis()
        emit('game/end', to=room)


@socket_app.on('game/answer')
def game_on_answer(data):
    room = data['joining_code']
    print('answer', data)
    with game_access_lock:
        game = Game.get_game_from_redis(room)
        correct_answer_idx = game.current_question['correct_answer']
        correct_answer = game.current_question['answers'][correct_answer_idx]

        if data['answer'] == correct_answer:
            answer_score = min(10, int(data['time_left']))
            game.current_scores[str(session['user_id'])] += answer_score
            game.commit_to_redis()


@socket_app.on('game/request-answer')
def game_on_request_answer(data):
    room = data['joining_code']
    with game_access_lock:
        game = Game.get_game_from_redis(room)
        correct_answer_idx = game.current_question['correct_answer']
        correct_answer = game.current_question['answers'][correct_answer_idx]
        emit('game/correct-answer', correct_answer, to=room)


@socket_app.on('game/request-scores')
def game_on_request_scores(data):
    room = data['joining_code']
    backend_game = make_backend_request('get', f'games/{data["joining_code"]}').json()
    user_id_to_name = {
        player['id']: player['user_name'] for player in backend_game['players']
    }
    with game_access_lock:
        game = Game.get_game_from_redis(room)
        scores = [{'name': user_id_to_name[int(user_id)], 'score': score} for user_id, score in game.current_scores.items()]
        emit('game/scores', scores, to=room)


if __name__ == '__main__':
    socket_app.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
