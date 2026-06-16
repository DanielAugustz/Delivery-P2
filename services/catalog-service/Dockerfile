FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app/src
ENV PORT=5001
EXPOSE 5001

CMD sh -c "gunicorn --bind 0.0.0.0:${PORT} principal:app"
