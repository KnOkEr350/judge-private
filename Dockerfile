FROM python:3.11-slim

WORKDIR /app

COPY tests/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tests/ ./tests/
COPY tests/runner.py .


ENTRYPOINT ["python", "runner.py"]