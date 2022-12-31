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
from flask_socketio import SocketIO, emit, join_room, leave_room
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
    print(available_categories)
    available_categories.extend([{'id': 0, 'name': 'Any'}])
    return render_template('create_game.html', categories=available_categories)


@app.route('/create-game', methods=['POST'])
@login_required
def create_game():
    data = request.form.to_dict()
    data['host_player'] = session['user_id']
    response = make_backend_request('post', 'games/', data)
    if response.status_code == 201:
        flash('Game created successfully')
        # Create the game object
        game = Game(response.json()['joining_code'], data['max_players'], session['user_id'])
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
        backend_game = make_backend_request('get', f'games/{joining_code}').json()
        game = Game.get_game_from_redis(joining_code)
        game_players = [
            player['user_name'] for player in backend_game['players']
        ]
        game_host_id = backend_game['host_player']
        print(game_players)
        print(backend_game)
    except KeyError as e:
        flash('Game not found')
        print(str(e))
        return redirect(url_for('index'))
    return render_template('game_lobby.html', game=game, game_players=game_players, game_host_id=game_host_id)


@app.route('/start-game', methods=['POST'])
def start_game():
    data = request.form.to_dict()
    response = make_backend_request('post', f'games/{data["joining_code"]}/start')
    if response.status_code == 200:
        flash('Game started successfully')
        return redirect(url_for('game', joining_code=data['joining_code']))
    flash(f'Failed to start game: {response.json()["detail"]}')
    return redirect(url_for('index'))


@app.route('/leave-game', methods=['POST'])
def leave_game():
    data = request.form.to_dict()
    response = make_backend_request('post', f'games/{data["joining_code"]}/leave')
    if response.status_code == 200:
        flash('Game left successfully')
        return redirect(url_for('index'))
    flash(f'Failed to leave game: {response.json()["detail"]}')
    return redirect(url_for('index'))


@app.route('/cancel-game', methods=['POST'])
def cancel_game():
    data = request.form.to_dict()
    response = make_backend_request('post', f'games/{data["joining_code"]}/cancel')
    if response.status_code == 200:
        flash('Game cancelled successfully')
        return redirect(url_for('index'))
    flash(f'Failed to cancel game: {response.json()["detail"]}')
    return redirect(url_for('index'))


if __name__ == '__main__':
    socket_app.run(app, host='0.0.0.0', port=5000, debug=True)