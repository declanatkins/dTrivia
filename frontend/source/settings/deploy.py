import os


# Flask settings
FLASK_SECRET_KEY  = os.getenv("FLASK_SECRET")


# Redis settings
REDIS_HOST  = os.getenv("REDIS_HOST")
REDIS_PORT  = os.getenv("REDIS_PORT")
REDIS_PASSWORD  = os.getenv("REDIS_PASSWORD", "")
REDIS_DB  = os.getenv("REDIS_DB")


# Backend settings
BACKEND_URL = os.getenv("BACKEND_URL")