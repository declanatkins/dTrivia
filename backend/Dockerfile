FROM python:3.10.9-buster


COPY requirements.txt .
RUN pip install -r requirements.txt


COPY source /app
WORKDIR /app
# CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "4", "-k", "uvicorn.workers.UvicornWorker"]
CMD ["uvicorn", "app:app"]
