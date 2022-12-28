import os
from functools import wraps
from flask import session, flash, render_template
import requests
from settings import get_settings


settings = get_settings()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'session_id' not in session:
            flash('Login Required')
            return render_template('index.html')
        return func(*args, **kwargs)
    return wrapper


def make_backend_request(method, path, data=None, auth=True):
    if auth:
        return make_backend_request_with_auth(method, path, data)
    else:
        return make_backend_request_without_auth(method, path, data)


def make_backend_request_without_auth(method, path, data=None):
    methods = {
        'post': requests.post,
        'get': requests.get,
        'put': requests.put,
        'delete': requests.delete
    }
    try:
        method = methods[method]
    except KeyError:
        raise AttributeError('Unkown request type')
    
    url = os.path.join(settings.BACKEND_URL, path)
    response = method(url, json=data)
    return response


def make_backend_request_with_auth(method, path, data=None):
    methods = {
        'post': requests.post,
        'get': requests.get,
        'put': requests.put,
        'delete': requests.delete
    }
    try:
        method = methods[method]
    except KeyError:
        raise AttributeError('Unkown request type')
    
    headers = {
        'session-id': session['session_id']
    }

    url = os.path.join(settings.BACKEND_URL, path)
    if data is None:
        response = method(url, headers=headers)
    else:
        response = method(url, json=data, headers=headers)
    return response