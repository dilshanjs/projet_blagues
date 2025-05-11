# Dockerfile for Mini-API GCP project

# 1. Base image
FROM python:3.11-slim

# 2. Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONUNBUFFERED=True

# 3. Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Set work directory
WORKDIR /app

# 5. Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy application code
COPY . .

# 7. Expose the port Cloud Run will listen on
EXPOSE 8080

# 8. Start the app with Gunicorn
#    - Bind to 0.0.0.0:8080 for Cloud Run
#    - main:app assumes your Flask app instance is called 'app' in main.py
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
