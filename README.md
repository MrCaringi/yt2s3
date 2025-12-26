# YT-2-S3

Download a video from YT, convert it to MP3 audio format (with ffmpeg) and upload it to a S3 compatible storage (RustFS, minio, etc)

## Docker Hub repo

[Docker Hub Repository](https://hub.docker.com/r/mrcaringi/yt2s3)

## How to use:

### COMPOSE.YAML Example
```yaml
services:
  youtube-worker:
    image: mrcaringi/yt2s3:latest
    container_name: yt-dlp-worker
    volumes:
      - ./yt-dlp/cookies.txt:/app/cookies.txt
      - /tmp/yt-dlp:/tmp
    environment:
      - YTDLP_COOKIES=/app/cookies.txt
      - S3_ENDPOINT=${S3_ENDPOINT}
      - S3_ACCESS_KEY=${S3_ACCESS_KEY}
      - S3_SECRET_KEY=${S3_SECRET_KEY}
      - S3_SECURE=true
      - S3_OBJECT_PREFIX=audios
    ports:
      - 5000:5000
    restart: always
```
#### cookies.txt
This file must contain your cookies for your YouTube sessions in Netscape format.

You can get it, for instance, [using this plugin in your browser](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)

### EJS / JavaScript challenge runtime

- The container image now includes the Deno JavaScript runtime and installs `yt-dlp` with the default extras (including `yt-dlp-ejs`).
- Having a supported JS runtime and the EJS scripts available avoids the "challenge solving failed" warnings when downloading from YouTube.


### INPUT
- METHOD: `POST`
- URL: `http://youtube-worker:5000/process`
- BODY: __JSON Body content type__
```JSON
  {
    "videoId": "RFQi7QcVN74-16",
    "bucketName": "your S3 bucket Name"
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

- Version 2.0.1 — 2025-12-26
  - Using Gunicorn instead of Flask
- Version 2.0.0 — 2025-12-26
  - **BREAKING CHANGES**
    - Replaced MinIO-specific environment variables with generic `S3_*` names: `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_SECURE`.
    - Added `S3_OBJECT_PREFIX` environment variable to configure the upload path/prefix inside the bucket (default: `audios`).
  - Translated internal comments and Dockerfile docs to English.

</details>