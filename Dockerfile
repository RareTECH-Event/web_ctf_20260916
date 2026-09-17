FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY flags.py .
COPY app/ ./app/
COPY secret/ ./secret/

ENV FLASK_APP=app.main
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["flask", "run"]
