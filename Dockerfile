FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Build-time args to propagate the image/tag and repository URL into the image
ARG IMAGE_VERSION=dev
ARG DOCKER_REPO_URL=https://hub.docker.com/r/mrcaringi/yt2s3/tags

# Expose as environment variables inside the container and label the image
ENV IMAGE_VERSION=${IMAGE_VERSION}
ENV DOCKER_REPO_URL=${DOCKER_REPO_URL}
LABEL org.opencontainers.image.version="${IMAGE_VERSION}"
LABEL org.opencontainers.image.source="https://github.com/MrCaringi/yt2s3"

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
# Force upgrade yt-dlp to ensure latest EJS challenge solver scripts are available
RUN python -m pip install --upgrade --force-reinstall 'yt-dlp[default]'

# Install Deno runtime (used by yt-dlp EJS challenge solver)
# Install into /usr/local to avoid using a per-user home dir during image build
RUN curl -fsSL https://deno.land/x/install/install.sh | DENO_INSTALL=/usr/local sh && \
    chmod +x /usr/local/bin/deno

# Copy the application
WORKDIR /app
COPY . /app

# Add entrypoint script that prints version + repo once and then execs gunicorn
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose port (Flask)
EXPOSE 5000

# Entrypoint prints version once then starts Gunicorn
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
