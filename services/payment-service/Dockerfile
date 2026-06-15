FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app/src
EXPOSE 5002

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "principal:app"]
