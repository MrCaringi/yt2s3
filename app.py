import os
import requests
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from minio import Minio
import shutil
import tempfile
import glob

app = Flask(__name__)

# --- S3 / S3-compatible storage configuration ---
# The worker needs S3-compatible endpoint and credentials.
# Environment variables use generic names (S3_*) — these must be provided in Docker.
S3_ENDPOINT = os.environ.get("S3_ENDPOINT")  # e.g. s3.example.com
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
# Whether to use HTTPS when contacting the S3 endpoint (true/false)
S3_SECURE = os.environ.get("S3_SECURE", "true").lower() == "true"

# Path to the cookie file for yt-dlp (configurable via the YTDLP_COOKIES env var)
YTDLP_COOKIES = os.environ.get("YTDLP_COOKIES", "/app/cookies.txt")

# Configurable S3 object prefix (folder/path inside the bucket). Default: 'audios'
S3_OBJECT_PREFIX = os.environ.get("S3_OBJECT_PREFIX", "audios").strip('/')

def prepare_cookiefile(path):
    """If the cookiefile exists but is mounted read-only, copy it to a temp file
    so that yt-dlp can write to it. Returns the usable path or None.
    """
    if not path or not os.path.isfile(path):
        return None
    try:
        # if writable, use as-is
        if os.access(path, os.W_OK):
            return path
        # copy to tmp to allow yt-dlp to write
        tmp = tempfile.NamedTemporaryFile(prefix="yt_cookies_", delete=False)
        tmp.close()
        shutil.copy2(path, tmp.name)
        os.chmod(tmp.name, 0o600)
        return tmp.name
    except Exception as e:
        app.logger.warning(f"prepare_cookiefile failed: {e}")
        return None

@app.route('/process', methods=['POST'])
def process_video():
    """
    Download the video, convert it to MP3 and upload it to S3-compatible storage.
    """
    data = request.json
    video_id = data.get('videoId')
    bucket_name = data.get('bucketName')
    
    if not video_id or not bucket_name:
        app.logger.warning("Missing videoId or bucketName in request")
        return jsonify({"error": "Missing videoId or bucketName"}), 400

    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    temp_filepath = f"/tmp/{video_id}.mp3"
    # Use configured prefix for the S3 object (no leading/trailing slashes)
    s3_object_name = f"{S3_OBJECT_PREFIX}/{video_id}.mp3"

    app.logger.info("Start processing video=%s bucket=%s url=%s", video_id, bucket_name, youtube_url)

    try:
        # --- 1. DOWNLOAD & CONVERSION WITH YT-DLP ---
        cookiefile_to_use = None
        if os.path.isfile(YTDLP_COOKIES):
            cookiefile_to_use = prepare_cookiefile(YTDLP_COOKIES)
        else:
            app.logger.warning("cookies not found at %s; proceeding without cookies (may fail for some videos)", YTDLP_COOKIES)

        app.logger.info("yt-dlp options prepared (cookiefile=%s)", bool(cookiefile_to_use))

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '/tmp/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'quiet': True,
        }
        if cookiefile_to_use:
            ydl_opts['cookiefile'] = cookiefile_to_use

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
        except Exception as e:
            app.logger.exception("yt-dlp download failed for video=%s", video_id)
            return jsonify({"error": f"yt-dlp failed: {e}"}), 500

        # identify resulting file
        video_id = info.get('id') if isinstance(info, dict) else video_id
        title = info.get('title') if isinstance(info, dict) else None
        # optional metadata
        duration = info.get('duration') if isinstance(info, dict) else None
        uploader = info.get('uploader') if isinstance(info, dict) else None
        upload_date = info.get('upload_date') if isinstance(info, dict) else None
        expected_mp3 = f"/tmp/{video_id}.mp3" if video_id else None
        final_file = None
        if expected_mp3 and os.path.isfile(expected_mp3):
            final_file = expected_mp3
        else:
            if video_id:
                candidates = glob.glob(f"/tmp/{video_id}.*")
                mp3s = [c for c in candidates if c.endswith('.mp3')]
                if mp3s:
                    final_file = mp3s[0]
                elif candidates:
                    final_file = candidates[0]

        if not final_file or not os.path.isfile(final_file):
            app.logger.error("Expected output not found for id=%s; candidates=%s", video_id, glob.glob(f"/tmp/{video_id}.*"))
            return jsonify({"error": "download produced no usable file"}), 500

        file_size = os.path.getsize(final_file)
        app.logger.info("Download/convert complete for id=%s title=%s file=%s size=%s bytes", video_id, title, final_file, file_size)

        # --- 2. Upload directly to S3-compatible storage ---
        minio_client = Minio(
            S3_ENDPOINT,
            access_key=S3_ACCESS_KEY,
            secret_key=S3_SECRET_KEY,
            secure=S3_SECURE
        )

        app.logger.info("Uploading %s to bucket=%s object=%s", final_file, bucket_name, s3_object_name)
        result = minio_client.fput_object(
            bucket_name,
            s3_object_name,
            final_file,
            content_type='audio/mpeg'
        )

        # Log upload result (if available) and final URL
        try:
            etag = getattr(result, "etag", None) or getattr(result, "object", None)
        except Exception:
            etag = None
        final_url = f"http{'s' if S3_SECURE else ''}://{S3_ENDPOINT}/{bucket_name}/{s3_object_name}"
        app.logger.info("Upload successful for id=%s object=%s size=%s bytes etag=%s url=%s", video_id, s3_object_name, file_size, etag, final_url)

        # Clean up
        os.remove(final_file)
        if cookiefile_to_use and cookiefile_to_use != YTDLP_COOKIES:
            try:
                os.remove(cookiefile_to_use)
            except Exception:
                pass

        # Return detailed response including S3 object id/url and useful metadata
        return jsonify({
            "status": "success",
            "videoId": video_id,
            "title": title,
            "uploader": uploader,
            "upload_date": upload_date,
            "duration_seconds": duration,
            "size_bytes": file_size,
            "s3ObjectId": final_url,
            "s3Object": s3_object_name,
            "s3Url": final_url,
            "etag": etag
        }), 200

    except Exception as e:
        app.logger.exception("Processing failed for video=%s", video_id)
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

if __name__ == '__main__':
    # Bind to 0.0.0.0 so the service is reachable from other containers
    app.run(host='0.0.0.0', port=5000)
