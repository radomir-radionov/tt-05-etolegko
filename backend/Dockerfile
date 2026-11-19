FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/data

ENV DATABASE_URL=sqlite:////app/data/app.db

CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000