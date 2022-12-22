from functools import wraps
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


app = Flask(__name__)
settings = get_settings()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response = make_backend_request('post', 'login', data)
    if response.status_code == 200:
        session['session_id'] = response.json()['session_id']
    else:
        flash('Invalid Credentials')
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    make_backend_request('post', 'logout')
    session.pop('session_id')
    return redirect(url_for('index'))
