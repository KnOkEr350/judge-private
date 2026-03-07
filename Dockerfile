FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pytest==8.* httpx==0.27.*

COPY test_private.py .

CMD ["pytest", "test_private.py", "-v", "--tb=short"]