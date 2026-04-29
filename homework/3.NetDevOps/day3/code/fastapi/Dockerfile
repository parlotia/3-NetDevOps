FROM docker.m.daocloud.io/library/python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY fastapi.crt .
COPY fastapi.key .

EXPOSE 443

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "443", "--ssl-keyfile", "fastapi.key", "--ssl-certfile", "fastapi.crt"]
