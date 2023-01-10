import os

# Postgres settings
DB_HOST  = "localhost"
DB_PORT  = "5432"
DB_NAME  = os.getenv("DB_NAME","dtrivia-dev")
DB_USER  = os.getenv("DB_USER", "postgres")
DB_PASSWORD  = os.getenv("DB_PASSWORD")


# FastAPI settings
API_HOST  = "localhost"
API_PORT  = "8000"


# Redis settings
REDIS_HOST  = "localhost"
REDIS_PORT  = "6379"
REDIS_PASSWORD  = os.getenv("REDIS_PASSWORD", "")
REDIS_DB  = "0"