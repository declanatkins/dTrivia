from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_socketio import SocketIO, emit, join_room, leave_room
from settings import get_settings


app = Flask(__name__)
settings = get_settings()


@app.route('/')
def index():
    return render_template('index.html')