import os

# Postgres settings
DB_HOST  = "localhost"
DB_PORT  = "5432"
DB_NAME  = "dtrivia-dev"
DB_USER  = os.getenv("DB_USER")
DB_PASSWORD  = os.getenv("DB_PASSWORD")


# FastAPI settings
API_HOST  = "localhost"
API_PORT  = "8000"
