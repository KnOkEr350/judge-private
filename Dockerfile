FROM python:3.11-slim

WORKDIR /app

COPY test_private.py .


RUN pip install --no-cache-dir pytest httpx

CMD ["pytest", "test_private.py", "-v", "--tb=short"]