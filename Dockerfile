
FROM python:3.12-slim

WORKDIR /app

COPY main.py .
COPY sample_logs ./sample_logs

CMD ["python", "main.py"]
