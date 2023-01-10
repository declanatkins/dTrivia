FROM python:3.10.9-buster


COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt


COPY source /app
WORKDIR /app


CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "1", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"]
