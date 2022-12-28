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


EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


app = Flask(__name__)
settings = get_settings()
app.secret_key = settings.FLASK_SECRET_KEY


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
    if response.status_code == 200:
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
    response = make_backend_request('post', 'games/join', data)
    if response.status_code == 200:
        flash('Game joined successfully')
        return redirect(url_for('game_lobby', joining_code=response.json()['joining_code']))
    flash(f'Failed to join game: {response.json()["detail"]}')
    return redirect(url_for('index'))


@app.route('/game/<joining_code>/lobby', methods=['GET'])
@login_required
def game_lobby(joining_code):
    response = make_backend_request('get', f'games/{joining_code}')
    if response.status_code == 200:
        return render_template('game-lobby.html', game=response.json())
    else:
        flash(f'Failed to get game: {response.json()["detail"]}')
        return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)