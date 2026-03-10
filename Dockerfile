FROM python:3.11-slim

WORKDIR /app


RUN pip install --no-cache-dir pytest-asyncio==1.* httpx==0.27.*

COPY tests/ ./tests/
COPY tests/runner.py .


ENTRYPOINT ["python", "runner.py"]