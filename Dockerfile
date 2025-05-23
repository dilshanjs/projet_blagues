# Dockerfile for Générateur de Blagues

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

# 5. Create a non-root user
RUN useradd -m -u 1000 appuser

# 6. Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy application code
COPY . .

# 8. Create logs directory and set permissions
RUN mkdir -p logs && chown -R appuser:appuser /app

# 9. Switch to non-root user
USER appuser

# 10. Expose the port the app will listen on
EXPOSE 8080

# 11. Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/mini-projet-459407-5eeaa3b13b0e.json
ENV PROJECT_ID="mini-projet-459407"
ENV LOCATION="europe-west1"

# 12. Start the app with Flask
CMD ["python", "main.py"]
