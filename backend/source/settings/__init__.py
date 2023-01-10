import os
from . import deploy, local


def get_settings():
    if os.environ.get('DEPLOY', False):
        return deploy
    else:
        return local
    