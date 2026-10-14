
FROM python:3.12-slim

WORKDIR /app

# Install application dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and frontend
COPY app.py .
COPY main.py .
COPY templates ./templates
COPY sample_logs ./sample_logs

# Flask web server port
EXPOSE 5000

# Run Flask so it is accessible outside the container
CMD ["python", "-c", "from app import app; app.run(host='0.0.0.0', port=5000, debug=False)"]
