FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Install system dependencies (ffmpeg and basic tools)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        ca-certificates \
        curl \
        unzip \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip setuptools
RUN python -m pip install 'yt-dlp[default]' flask requests minio gunicorn

# Install Deno runtime (used by yt-dlp EJS challenge solver)
# Install into /usr/local to avoid using a per-user home dir during image build
RUN curl -fsSL https://deno.land/x/install/install.sh | DENO_INSTALL=/usr/local sh && \
    chmod +x /usr/local/bin/deno

# Copy the application
WORKDIR /app
COPY . /app

# Expose port (Flask)
EXPOSE 5000

# Default command: run with Gunicorn (production WSGI server)
# Removes Flask development server warning and the "Press CTRL+C to quit" message
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "2", "--threads", "4", "--log-level", "info", "--capture-output", "--log-file", "-", "--access-logfile", "-"]
