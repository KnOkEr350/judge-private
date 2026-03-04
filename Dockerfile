FROM python:3.11-slim

WORKDIR /app

COPY test_private.py .

RUN pip install pytest fastapi httpx

ENV PYTHONPATH=/student

CMD ["pytest", "test_private.py", "-v", "--tb=short"]

