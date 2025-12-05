import os
import subprocess
import sys
import tempfile


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
    temp_fd, temp_file = tempfile.mkstemp(suffix='.mp3', dir=os.path.dirname(input_file))
    os.close(temp_fd)
    
    # Build ffmpeg command with loudnorm filter
    # Using single-pass normalization (faster, slightly less accurate than two-pass)
    # Target: -23 LUFS (EBU R128 broadcast standard, similar to MP3Gain default)
    cmd = [
        ffmpeg_path,
        "-i", input_file,
        "-af", f"loudnorm=I={target_lufs}:TP=-2.0:LRA=11",
        "-ar", "44100",  # Maintain sample rate
        "-y",  # Overwrite output file
        temp_file
    ]
    
    # Run ffmpeg (suppress output)
    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
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
        if f.lower().endswith('.mp3') and os.path.isfile(os.path.join(output_dir, f))
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

