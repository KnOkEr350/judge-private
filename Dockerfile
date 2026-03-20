FROM python:3.11-slim

WORKDIR /app

RUN mkdir -p /tests/app

COPY tests/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY tests/ ./tests/
COPY tests/runner.py .


RUN chmod -R 777 /app
ENTRYPOINT ["python", "runner.py"]