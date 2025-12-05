import os
import sys
import argparse
import shutil
import yt_dlp
from tqdm import tqdm

from src.ffmpeg_utils import get_ffmpeg_path
from src.audio_normalize import normalize_all_mp3_files, validate_audio_duration


def download_playlist_as_mp3(
    playlist_url, bitrate="320", ffmpeg_path=None, normalize=True
):
    """
    Download all videos from a YouTube playlist as MP3 files at specified bitrate.

    Args:
        playlist_url (str): URL of the YouTube playlist
        bitrate (str): Audio bitrate in kbps, default is "320"
        ffmpeg_path (str): Path to ffmpeg executable (optional, will use PATH if not provided)
        normalize (bool): Whether to normalize audio volume after download (default: True)
    """
    # Get the repository root directory (where the script is located)
    repo_root = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(repo_root, "musique")

    # Clean output directory: remove all existing files before downloading
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        print(f"Cleaned output directory: {output_dir}")
    else:
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Detect if URL is a single video (contains v= parameter) or a playlist
    # If URL contains v=, force single video download even if list= is present
    is_single_video = "v=" in playlist_url

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

    # First, extract playlist info to get total number of videos
    info_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "noplaylist": is_single_video,
    }

    with yt_dlp.YoutubeDL(info_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        if "entries" in info:
            total_videos = len([e for e in info["entries"] if e is not None])
        else:
            total_videos = 1

    # Initialize progress bar
    pbar = tqdm(
        total=total_videos,
        desc="Downloading",
        unit="track",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
    )

    # Track downloaded videos to avoid counting duplicates
    downloaded_files = set()

    def progress_hook(d):
        """
        Progress hook to update the progress bar when a video download completes.
        """
        if d["status"] == "finished":
            filename = d.get("filename", "")
            # Only count once per file (avoid counting both download and post-processing)
            if filename and filename not in downloaded_files:
                downloaded_files.add(filename)
                # Extract just the filename without path for cleaner display
                display_name = os.path.basename(filename)
                # Truncate if too long
                if len(display_name) > 40:
                    display_name = display_name[:37] + "..."
                pbar.set_postfix_str(display_name)
                pbar.update(1)

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
        "quiet": True,  # Hide download logs
        "no_warnings": True,  # Hide warnings
        "ignoreerrors": False,  # Fail-fast: stop on errors
        "noplaylist": is_single_video,  # If single video URL, don't download playlist
        "extract_flat": False,  # Extract all videos in the playlist
        "writethumbnail": False,
        "writeinfojson": False,
        "writedescription": False,
        # Specify ffmpeg location for postprocessors
        "ffmpeg_location": ffmpeg_location,
        # Use native HLS downloader (more reliable than external ffmpeg for HLS)
        "hls_use_mpegts": True,  # Use MPEG-TS container for HLS (better compatibility)
        # Retry on errors
        "retries": 10,
        "fragment_retries": 10,
        # Progress hook
        "progress_hooks": [progress_hook],
    }

    # Download the playlist
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([playlist_url])

    # Close progress bar
    pbar.close()

    if error_code != 0:
        print(f"\nERROR: Playlist download failed with error code: {error_code}")
        sys.exit(1)

    print("\nPlaylist download completed successfully!")

    # Normalize audio volume if requested
    if normalize:
        normalize_all_mp3_files(output_dir, ffmpeg_path)

    # Validate that all files are under 79 minutes
    validate_audio_duration(output_dir, ffmpeg_path, max_duration_minutes=79)


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
    parser.add_argument(
        "--no-normalize", action="store_true", help="Skip audio volume normalization"
    )

    args = parser.parse_args()
    download_playlist_as_mp3(
        args.playlist_url, args.bitrate, ffmpeg_path, normalize=not args.no_normalize
    )
