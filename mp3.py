import os
import sys
import argparse
import shutil
import yt_dlp


def check_ffmpeg_available():
    """
    Check if ffmpeg is available in the system PATH.
    Fail-fast if not available since it's required for audio conversion.
    """
    if shutil.which("ffmpeg") is None:
        print("ERROR: ffmpeg is not installed or not in PATH.")
        print("ffmpeg is required for audio conversion to MP3.")
        print("\nInstallation instructions:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")
        sys.exit(1)


def download_playlist_as_mp3(playlist_url, bitrate="320"):
    """
    Download all videos from a YouTube playlist as MP3 files at specified bitrate.

    Args:
        playlist_url (str): URL of the YouTube playlist
        bitrate (str): Audio bitrate in kbps, default is "320"
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
        # Force use of ffmpeg for HLS downloads instead of hlsnative (avoids 403 errors)
        "hls_use_mpegts": True,  # Use MPEG-TS container for HLS (better compatibility)
        "hls_prefer_native": False,  # Disable native HLS downloader, use ffmpeg instead
        "external_downloader": "ffmpeg",  # Use ffmpeg for all downloads including HLS
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
    # Fail-fast: check ffmpeg availability before proceeding
    check_ffmpeg_available()

    parser = argparse.ArgumentParser(
        description="Download YouTube playlist videos as MP3s"
    )
    parser.add_argument("playlist_url", help="URL of the YouTube playlist")
    parser.add_argument(
        "-b", "--bitrate", default="320", help="Audio bitrate in kbps (default: 320)"
    )

    args = parser.parse_args()
    download_playlist_as_mp3(args.playlist_url, args.bitrate)
