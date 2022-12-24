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
from utils import login_required, make_backend_request, make_backend_request_without_auth


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)