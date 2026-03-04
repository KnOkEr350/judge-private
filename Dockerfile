FROM python:3.12-slim

WORKDIR /app

RUN pip install pytest fastapi httpx

COPY test_private.py /app/test_private.py

ENV PYTHONPATH="/student"

CMD ["pytest", "test_private.py", "-v"]