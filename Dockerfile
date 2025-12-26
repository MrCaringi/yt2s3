FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Install system dependencies (ffmpeg and basic tools)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        ca-certificates \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip setuptools
RUN pip install yt-dlp flask requests minio

# Copy the application
WORKDIR /app
COPY . /app

# Expose port (Flask)
EXPOSE 5000

# Default command
CMD ["python", "app.py"]
