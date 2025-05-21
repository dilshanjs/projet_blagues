# Dockerfile for Mini-API GCP project

# 1. Base image
FROM python:3.9-slim

# 2. Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONUNBUFFERED=True

# 3. Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Set work directory
WORKDIR /app

# 5. Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy application code
COPY . .

# 7. Copy Google Cloud credentials
COPY mini-projet-459407-5eeaa3b13b0e.json .

# 8. Expose the port Cloud Run will listen on
EXPOSE 5000

# 9. Set Flask environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/mini-projet-459407-5eeaa3b13b0e.json
ENV PROJECT_ID="mini-projet-459407"
ENV LOCATION="us-central1"

# 10. Start the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "main:app"]
