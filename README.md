# YT-2-S3

Download a video from YT in MP3 audio format and upload it to a S3 compatible storage (RustFS, minio, etc)

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
      # EJS Challenge Solver (v2.4.0+) — downloads latest scripts from GitHub for YouTube compatibility
      - YTDLP_REMOTE_COMPONENTS=ejs:github
      # Optional yt-dlp/ffmpeg tuning (uncomment to customize):
      #- YTDLP_FORMAT=bestaudio/best
      #- YTDLP_PREFERRED_CODEC=mp3
      #- YTDLP_PREFERRED_QUALITY=128
      #- YTDLP_POSTPROCESSOR_ARGS=-loglevel info
    ports:
      - 5000:5000
    restart: always
```

#### .env file example
Create a `.env` file in the same directory as your `docker-compose.yml`:
```bash
# S3 credentials and endpoint
S3_ENDPOINT=s3.example.com
S3_ACCESS_KEY=your_access_key
S3_SECRET_KEY=your_secret_key
S3_SECURE=true

# Optional: tune yt-dlp/ffmpeg behavior
# YTDLP_FORMAT=bestaudio/best
# YTDLP_PREFERRED_QUALITY=192
```

#### Parameters
- `/tmp/yt-dlp` is the directory used during file download; after upload to s3-storage, the file is deleted.
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

## Troubleshooting

### EJS Challenge Solver Errors (v2.4.0+)

If you encounter errors like:
- `Hash mismatch on challenge solver core script`
- `Challenge solver lib script version X.X.X is not supported`
- `The downloaded file is empty`
- `Requested format is not available`

**Root cause:**
YouTube uses JavaScript challenges to verify legitimate download requests. yt-dlp requires up-to-date EJS (JavaScript challenge solver) scripts to handle these challenges. If the scripts are outdated, YouTube blocks the download.

**Solutions (in order of preference):**

1. **Ensure you're using v2.4.0 or later** (recommended):
   - The container now automatically downloads the latest EJS scripts from GitHub on first run
   - Make sure `YTDLP_REMOTE_COMPONENTS` is NOT set to an empty value (default: `ejs:github`)
   - The container needs internet connectivity to download these scripts
   - Example compose configuration:
     ```yaml
     services:
       yt2s3:
         image: mrcaringi/yt2s3:2.4.0  # Use 2.4.0 or later
         environment:
           - YTDLP_REMOTE_COMPONENTS=ejs:github  # Default, explicitly shown
     ```

### HTTP 403 Forbidden error from YouTube

If you encounter errors like `[download] Got error: HTTP Error 403: Forbidden`, this typically indicates that YouTube is blocking the download request. This can happen for several reasons:

**Root causes:**
- Your `cookies.txt` file is expired or outdated
- The video is from a channel that has additional protection or regional restrictions
- YouTube has changed its authentication/access patterns

**Solutions:**
1. **Update your cookies.txt** — The most common fix:
   - Use a browser cookie exporter extension (e.g., [Get CookiesTxt Locally](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) for Chrome/Edge)
   - Export your cookies in Netscape format from a YouTube session where you're logged in
   - Replace the `cookies.txt` file and restart the container
   - Cookies expire periodically; refresh them every 2-4 weeks for continuous operation

2. **Check for channel-specific restrictions:**
   - Try downloading from other channels to confirm it's not a global issue
   - Some channels may have stricter protection that requires additional authentication

3. **Use a custom User-Agent** (for advanced cases):
   - Set `YTDLP_EXTRA_OPTS_JSON` environment variable:
     ```yaml
     YTDLP_EXTRA_OPTS_JSON='{ "http_headers": { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" } }'
     ```

## Changelog
<details>
  <summary>Display changelog</summary>

- Version 2.4.1 — 2026-03-05
  - **MAJOR FIX**: Resolved YouTube download failures caused by a failure of usaje of `ytdlp_remote_components`

- Version 2.4.0 — 2026-02-08
  - **MAJOR FIX**: Resolved YouTube download failures caused by outdated EJS (JavaScript challenge solver) scripts. This addresses the "Hash mismatch on challenge solver core script" and "Challenge solver lib script version not supported" errors.
  - **Key Changes**:
    - Dockerfile now forces a reinstall of yt-dlp to ensure the latest version with updated EJS scripts
    - Added new environment variable `YTDLP_REMOTE_COMPONENTS` (default: `ejs:github`) which enables automatic download of the latest EJS challenge solver scripts directly from GitHub
    - Added `allowed_extractors: ['youtube']` to optimize yt-dlp options for YouTube
    - Added `yt_dlp_allow_breaks: True` to allow latest API functionality
  - **Breaking Changes**: None — these are backward-compatible improvements
  - **Migration Notes**: 
    - If you prefer NOT to auto-download remote components, set `YTDLP_REMOTE_COMPONENTS=` (empty string) in your environment, but this is **not recommended**
    - Default behavior now requires internet connectivity to download EJS scripts on first run (subsequent runs use cached scripts)
  - This resolves the issue where YouTube videos would fail with "The downloaded file is empty" or "Requested format is not available" errors

- Version 2.3.1 — 2026-01-17
  - **BUG FIX**: Fixed `UnboundLocalError` in the `finally` block that would occur when yt-dlp download fails. Variables `final_file` and `cookiefile_to_use` are now properly initialized at the start of the request handler.
  - This is NOT a breaking change; it only fixes a bug in error handling.

- Version 2.3.0 — 2026-01-01
  - Added configurable `yt-dlp` and `ffmpeg` options via environment variables so download/convert behavior can be tuned at runtime.
  - New environment variables (defaults shown):
    - `YTDLP_FORMAT` (default: `bestaudio/best`)
    - `YTDLP_OUTTMPL` (default: `/tmp/%(id)s.%(ext)s`)
    - `YTDLP_PREFERRED_CODEC` (default: `mp3`)
    - `YTDLP_PREFERRED_QUALITY` (default: `128`)
    - `YTDLP_POSTPROCESSOR_ARGS` (default: `-loglevel info`) — parsed into a list for ffmpeg args
    - `YTDLP_EXTRA_OPTS_JSON` (optional) — pass a JSON object of additional yt-dlp options that will be merged into the runtime options
  - New behavior is backwards-compatible: if no env vars are provided, previous defaults are used (NOT a breaking change).
  - Examples:
    - `docker run -e YTDLP_FORMAT="bestaudio[ext=m4a]" -e YTDLP_PREFERRED_QUALITY=192 mrcaringi/yt2s3:v2.3.0`
    - `docker-compose` (build or image) can set `environment` with any of the variables above.

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
