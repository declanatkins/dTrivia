import os


# Flask settings
FLASK_HOST  = "localhost"
FLASK_PORT  = "5000"
FLASK_SECRET_KEY  = os.getenv("FLASK_SECRET", "secret")


# Redis settings
REDIS_HOST  = "localhost"
REDIS_PORT  = "6379"
REDIS_PASSWORD  = os.getenv("REDIS_PASSWORD", "")
REDIS_DB  = "0"


# Backend settings
BACKEND_URL = "http://localhost:8000"
