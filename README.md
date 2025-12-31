# YT-2-S3

Download a video from YT, convert it to MP3 audio format (with ffmpeg) and upload it to a S3 compatible storage (RustFS, minio, etc)

## Docker Hub repo

[Docker Hub Repository](https://hub.docker.com/r/mrcaringi/yt2s3)

## How to use:

### COMPOSE.YAML Example
```yaml
services:
  yt2s3:
    image: mrcaringi/yt2s3:latest
    container_name: yt2s3
    volumes:
      - ./cookies.txt:/app/cookies.txt
      - /tmp/yt-dlp:/tmp
    environment:
      - YTDLP_COOKIES=/app/cookies.txt
      - S3_ENDPOINT=${S3_ENDPOINT}
      - S3_ACCESS_KEY=${S3_ACCESS_KEY}
      - S3_SECRET_KEY=${S3_SECRET_KEY}
      - S3_SECURE=true
    ports:
      - 5000:5000
    restart: always
```
#### Parameters
- `/tmp/yt-dlp` is the directory used during file download, after upload to s3-storage, the faile is deleted.
- `./cookies.txt` location of cookie file, see next section:
#### YTDLP_COOKIES / cookies.txt
This file must contain your cookies for your YouTube sessions in Netscape format.

You can get it, for instance, [using this plugin in your browser](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)

### EJS / JavaScript challenge runtime

- The container image now includes the Deno JavaScript runtime and installs `yt-dlp` with the default extras (including `yt-dlp-ejs`).
- Having a supported JS runtime and the EJS scripts available avoids the "challenge solving failed" warnings when downloading from YouTube.


### INPUT
- METHOD: `POST`
- URL: `http://yt2s3:5000/process`
- BODY: __JSON Body content type__
```JSON
  {
    "videoId": "RFQi7QcVN74",
    "bucketName": "your S3 bucket Name",
    "s3ObjectPrefix": "audios"
  }
```

### OUTPUT
```JSON
[
  {
    "duration_seconds": 4934,
    "etag": "cb9437dd9323e4483f6a66857183035b-16",
    "s3Object": "audios/RFQi7QcVN74.mp3",
    "s3ObjectId": "https://s3-endpoint.com/youtube/audios/RFQi7QcVN74.mp3",
    "s3Url": "https://s3-endpoint.com/youtube/audios/RFQi7QcVN74.mp3",
    "size_bytes": 78938843,
    "status": "success",
    "title": "EN VIVO - Dante Gebel #947 | Confesiones de un hombre dañado",
    "upload_date": "20251026",
    "uploader": "Dante Gebel",
    "videoId": "RFQi7QcVN74"
  }
]
```


## Contributors

<a href="https://github.com/MrCaringi/yt2s3/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=MrCaringi/yt2s3" />
</a>

[contrib.rocks](https://contrib.rocks).

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=MrCaringi/yt2s3&type=Date)](https://www.star-history.com/#MrCaringi/yt2s3&Date)

## Changelog
<details>
  <summary>Display changelog</summary>

- Version 2.2.1 — 2025-12-31
  - Github Actions update to automatically generate a release
- Version 2.2.0 — 2025-12-31
  - Moved startup/version logging to the container entrypoint so the message is printed exactly once and appears before Gunicorn's startup lines in container logs (avoids duplicate lines when running under Gunicorn).
  - Added `docker-entrypoint.sh` which prints the `IMAGE_VERSION` and `DOCKER_REPO_URL` (both can be provided via build-args) and then execs Gunicorn.
  - The previous in-app startup log was removed to prevent duplicate log entries from multiple processes.
  - This is NOT a breaking change.
- Version 2.1.4 — 2025-12-31
  - Added startup logging of the container image version and Docker Hub repository URL so the image tag is visible in container logs.
  - The image now accepts a build-time `IMAGE_VERSION` build-arg which is propagated into the running container as the `IMAGE_VERSION` environment variable and recorded in the OCI image label `org.opencontainers.image.version`.
  - The `DOCKER_REPO_URL` build-arg (default: `https://hub.docker.com/r/mrcaringi/yt2s3/tags`) is also set in the image and logged at startup.
  - This is NOT a breaking change; runtime behavior and API are unchanged.
- Version 2.1.3 — 2025-12-26
  - **BREAKING CHANGE**: `s3ObjectPrefix` is now required in the POST request JSON body and will be used as the upload prefix for that request. The server will reject requests without this field.
  - now logs yt-dlp download progress and routes yt-dlp messages into the Docker logs (via Flask logger). It also passes -loglevel info to ffmpeg so conversion activity appears
  - If you want more/less detail, adjust the postprocessor_args loglevel (quiet, info, warning, error) or change what the progress hook logs.
  - remove downloaded temporary file after upload to S3-Storage
- Version 2.0.3 — 2025-12-26
  - Update Dockerfile to use Gunicorn and include Deno runtime
- Version 2.0.0 — 2025-12-26
  - **BREAKING CHANGES**
    - Replaced MinIO-specific environment variables with generic `S3_*` names: `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_SECURE`.
    - Added `S3_OBJECT_PREFIX` environment variable to configure the upload path/prefix inside the bucket (default: `audios`).
  - Translated internal comments and Dockerfile docs to English.
</details>