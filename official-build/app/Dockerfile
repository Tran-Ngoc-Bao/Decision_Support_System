FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY app/ .

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]