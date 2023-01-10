import os

# Postgres settings
DB_HOST  = os.getenv("DB_HOST")
DB_PORT  = os.getenv("DB_PORT")
DB_NAME  = os.getenv("DB_NAME")
DB_USER  = os.getenv("DB_USER")
DB_PASSWORD  = os.getenv("DB_PASSWORD")


# Redis settings
REDIS_HOST  = os.getenv("REDIS_HOST")
REDIS_PORT  = os.getenv("REDIS_PORT")
REDIS_PASSWORD  = os.getenv("REDIS_PASSWORD")
REDIS_DB  = os.getenv("REDIS_DB")