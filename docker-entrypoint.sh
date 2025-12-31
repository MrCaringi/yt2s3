#!/bin/sh
set -e
# Print a concise startup line (once) so it's clearly visible in container logs
TS=$(date -u '+%Y-%m-%d %H:%M:%S %z')
IMAGE_VERSION=${IMAGE_VERSION:-dev}
DOCKER_REPO_URL=${DOCKER_REPO_URL:-https://hub.docker.com/r/mrcaringi/yt2s3/tags}
printf "[%s] yt2s3 startup: version=%s repo=%s\n" "$TS" "$IMAGE_VERSION" "$DOCKER_REPO_URL" >&2

# Exec Gunicorn (preserve args from Dockerfile style)
exec gunicorn --bind 0.0.0.0:5000 app:app --workers 2 --threads 4 --log-level info --capture-output --log-file - --access-logfile -
