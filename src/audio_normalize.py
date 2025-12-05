import os
import subprocess
import sys
import tempfile
import shutil


def normalize_audio_volume(input_file, ffmpeg_path, target_lufs=-23.0):
    """
    Normalize audio volume using ffmpeg loudnorm filter (EBU R128 standard).
    Similar to MP3Gain but using modern loudness normalization.

    Args:
        input_file (str): Path to input audio file
        ffmpeg_path (str): Path to ffmpeg executable
        target_lufs (float): Target integrated loudness in LUFS (default: -23.0, EBU R128 standard)

    Returns:
        bool: True if normalization succeeded, False otherwise
    """
    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    # Create temporary file for output
    temp_fd, temp_file = tempfile.mkstemp(
        suffix=".mp3", dir=os.path.dirname(input_file)
    )
    os.close(temp_fd)

    # Build ffmpeg command with loudnorm filter
    # Using single-pass normalization (faster, slightly less accurate than two-pass)
    # Target: -23 LUFS (EBU R128 broadcast standard, similar to MP3Gain default)
    cmd = [
        ffmpeg_path,
        "-i",
        input_file,
        "-af",
        f"loudnorm=I={target_lufs}:TP=-2.0:LRA=11",
        "-ar",
        "44100",  # Maintain sample rate
        "-y",  # Overwrite output file
        temp_file,
    ]

    # Run ffmpeg (suppress output)
    result = subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True
    )

    if result.returncode != 0:
        print(f"ERROR: Failed to normalize {os.path.basename(input_file)}")
        print(f"ffmpeg error: {result.stderr}")
        os.remove(temp_file)
        sys.exit(1)

    # Replace original file with normalized version
    os.replace(temp_file, input_file)
    return True


def normalize_all_mp3_files(output_dir, ffmpeg_path, target_lufs=-23.0):
    """
    Normalize volume of all MP3 files in a directory.

    Args:
        output_dir (str): Directory containing MP3 files
        ffmpeg_path (str): Path to ffmpeg executable
        target_lufs (float): Target integrated loudness in LUFS (default: -23.0)
    """
    if not os.path.exists(output_dir):
        print(f"ERROR: Output directory not found: {output_dir}")
        sys.exit(1)

    # Find all MP3 files
    mp3_files = [
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.lower().endswith(".mp3") and os.path.isfile(os.path.join(output_dir, f))
    ]

    if not mp3_files:
        print("No MP3 files found to normalize.")
        return

    print(f"\nNormalizing volume for {len(mp3_files)} file(s)...")
    print(f"Target loudness: {target_lufs} LUFS (EBU R128 standard)")

    for i, mp3_file in enumerate(mp3_files, 1):
        filename = os.path.basename(mp3_file)
        print(f"[{i}/{len(mp3_files)}] Normalizing: {filename}")
        normalize_audio_volume(mp3_file, ffmpeg_path, target_lufs)

    print("\nVolume normalization completed successfully!")


def get_audio_duration(file_path, ffmpeg_path):
    """
    Get audio file duration in seconds using ffprobe or ffmpeg.

    Args:
        file_path (str): Path to audio file
        ffmpeg_path (str): Path to ffmpeg executable

    Returns:
        float: Duration in seconds
    """
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)

    # Try ffprobe first (more accurate)
    ffprobe_path = None
    if ffmpeg_path:
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        ffprobe_path = os.path.join(ffmpeg_dir, "ffprobe")
        if not os.path.exists(ffprobe_path):
            ffprobe_path = shutil.which("ffprobe")
    else:
        ffprobe_path = shutil.which("ffprobe")

    # Use ffprobe if available
    if ffprobe_path:
        cmd = [
            ffprobe_path,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
    else:
        # Fallback to ffmpeg (use -f null to avoid creating output file)
        cmd = [
            ffmpeg_path if ffmpeg_path else "ffmpeg",
            "-i",
            file_path,
            "-f",
            "null",
            "-",
        ]

    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if result.returncode != 0:
        print(f"ERROR: Failed to get duration for {os.path.basename(file_path)}")
        print(f"Error: {result.stderr}")
        sys.exit(1)

    if ffprobe_path:
        # ffprobe returns duration as string
        duration_str = result.stdout.strip()
        if not duration_str:
            print(
                f"ERROR: Could not extract duration from {os.path.basename(file_path)}"
            )
            sys.exit(1)
        return float(duration_str)
    else:
        # Parse ffmpeg output: Duration: HH:MM:SS.mm
        stderr = result.stderr
        for line in stderr.split("\n"):
            if "Duration:" in line:
                duration_str = line.split("Duration:")[1].split(",")[0].strip()
                parts = duration_str.split(":")
                if len(parts) != 3:
                    print(
                        f"ERROR: Could not parse duration from {os.path.basename(file_path)}"
                    )
                    sys.exit(1)
                hours = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds

    print(f"ERROR: Could not extract duration from {os.path.basename(file_path)}")
    sys.exit(1)


def format_duration(seconds):
    """
    Format duration in seconds to MM:SS or HH:MM:SS format.

    Args:
        seconds (float): Duration in seconds

    Returns:
        str: Formatted duration string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def validate_audio_duration(output_dir, ffmpeg_path, max_duration_minutes=79):
    """
    Validate that all MP3 files are shorter than the maximum duration.

    Args:
        output_dir (str): Directory containing MP3 files
        ffmpeg_path (str): Path to ffmpeg executable
        max_duration_minutes (int): Maximum duration in minutes (default: 79)
    """
    if not os.path.exists(output_dir):
        print(f"ERROR: Output directory not found: {output_dir}")
        sys.exit(1)

    # Find all MP3 files
    mp3_files = [
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.lower().endswith(".mp3") and os.path.isfile(os.path.join(output_dir, f))
    ]

    if not mp3_files:
        print("No MP3 files found to validate.")
        return

    max_duration_seconds = max_duration_minutes * 60
    invalid_files = []

    print(f"\nValidating duration for {len(mp3_files)} file(s)...")
    print(f"Maximum allowed duration: {max_duration_minutes} minutes")

    for mp3_file in mp3_files:
        filename = os.path.basename(mp3_file)
        duration = get_audio_duration(mp3_file, ffmpeg_path)
        duration_minutes = duration / 60

        if duration > max_duration_seconds:
            invalid_files.append((filename, duration_minutes))

    if invalid_files:
        print(
            f"\n❌ ERROR: {len(invalid_files)} file(s) exceed the maximum duration of {max_duration_minutes} minutes:"
        )
        for filename, duration_min in invalid_files:
            print(
                f"  - {filename}: {duration_min:.2f} minutes ({format_duration(duration_min * 60)})"
            )
        sys.exit(1)
    else:
        print(f"\n✅ All files are valid (all under {max_duration_minutes} minutes)")
