import os
import sys
import argparse
import shutil
import yt_dlp

from src.ffmpeg_utils import get_ffmpeg_path


def download_playlist_as_mp3(playlist_url, bitrate="320", ffmpeg_path=None):
    """
    Download all videos from a YouTube playlist as MP3 files at specified bitrate.

    Args:
        playlist_url (str): URL of the YouTube playlist
        bitrate (str): Audio bitrate in kbps, default is "320"
        ffmpeg_path (str): Path to ffmpeg executable (optional, will use PATH if not provided)
    """
    # Get the repository root directory (where the script is located)
    repo_root = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(repo_root, "musique")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Configuration for yt-dlp
    # Format selector: prefer non-HLS audio formats, but fallback to HLS if needed
    format_selector = "bestaudio[ext!=m3u8][protocol!=m3u8_native]/bestaudio[ext!=m3u8]/bestaudio/best[ext!=m3u8][protocol!=m3u8_native]/best"

    # Configure ffmpeg location for yt-dlp
    # If using local binary, need to specify directory (not full path to binary)
    if ffmpeg_path and ffmpeg_path != shutil.which("ffmpeg"):
        # Extract directory from path
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        ffmpeg_location = ffmpeg_dir
    else:
        ffmpeg_location = None  # Use system PATH

    ydl_opts = {
        "format": format_selector,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": bitrate,
            }
        ],
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "verbose": False,
        "quiet": False,
        "no_warnings": False,
        "ignoreerrors": False,  # Fail-fast: stop on errors
        "noplaylist": False,  # Process the playlist
        "extract_flat": False,  # Extract all videos in the playlist
        "writethumbnail": False,
        "writeinfojson": False,
        "writedescription": False,
        # Specify ffmpeg location for postprocessors
        "ffmpeg_location": ffmpeg_location,
        # Force use of ffmpeg for HLS downloads instead of hlsnative (avoids 403 errors)
        "hls_use_mpegts": True,  # Use MPEG-TS container for HLS (better compatibility)
        "hls_prefer_native": False,  # Disable native HLS downloader, use ffmpeg instead
        "external_downloader": (
            ffmpeg_path
            if ffmpeg_path and ffmpeg_path != shutil.which("ffmpeg")
            else "ffmpeg"
        ),
        "external_downloader_args": {
            "ffmpeg": [
                "-loglevel",
                "error",
                "-http_persistent",
                "false",
                "-seekable",
                "0",
            ]
        },
        # Retry on errors
        "retries": 10,
        "fragment_retries": 10,
    }

    # Download the playlist
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([playlist_url])

    if error_code != 0:
        print(f"\nERROR: Playlist download failed with error code: {error_code}")
        sys.exit(1)

    print("\nPlaylist download completed successfully!")


if __name__ == "__main__":
    # Get ffmpeg path (downloads automatically if not found)
    ffmpeg_path = get_ffmpeg_path()

    parser = argparse.ArgumentParser(
        description="Download YouTube playlist videos as MP3s"
    )
    parser.add_argument("playlist_url", help="URL of the YouTube playlist")
    parser.add_argument(
        "-b", "--bitrate", default="320", help="Audio bitrate in kbps (default: 320)"
    )

    args = parser.parse_args()
    download_playlist_as_mp3(args.playlist_url, args.bitrate, ffmpeg_path)
