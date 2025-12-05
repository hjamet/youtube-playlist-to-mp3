import os
import sys
import shutil
import platform
import urllib.request
import tarfile
import stat


def get_ffmpeg_path():
    """
    Get ffmpeg executable path. If not found in PATH, download a static binary locally.
    Returns the path to ffmpeg executable.
    """
    # First, check if ffmpeg is available in PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    # Get repository root directory
    # Get the directory where this module is located, then go up to repo root
    current_file = os.path.abspath(__file__)
    src_dir = os.path.dirname(current_file)
    repo_root = os.path.dirname(src_dir)
    local_ffmpeg_dir = os.path.join(repo_root, ".local", "ffmpeg")
    local_ffmpeg_bin = os.path.join(local_ffmpeg_dir, "ffmpeg")

    # Check if local binary already exists
    if os.path.exists(local_ffmpeg_bin) and os.access(local_ffmpeg_bin, os.X_OK):
        return local_ffmpeg_bin

    # Determine platform and architecture
    machine = platform.machine().lower()
    system = platform.system().lower()

    # Only support Linux for automatic download
    if system != "linux":
        print("ERROR: ffmpeg is not installed or not in PATH.")
        print("ffmpeg is required for audio conversion to MP3.")
        print("\nInstallation instructions:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")
        sys.exit(1)

    # Map architecture to download URL
    arch_map = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "armv7l": "armhf",
        "armv6l": "armel",
    }

    arch = arch_map.get(machine, "amd64")
    if arch not in ["amd64", "arm64", "armhf", "armel"]:
        print(f"ERROR: Unsupported architecture: {machine}")
        print("Please install ffmpeg manually.")
        sys.exit(1)

    # Download URL for static ffmpeg builds (johnvansickle.com)
    # Using a reliable source for static Linux builds
    base_url = "https://johnvansickle.com/ffmpeg/releases"
    filename = f"ffmpeg-release-{arch}-static.tar.xz"
    url = f"{base_url}/{filename}"

    print(f"ffmpeg not found in PATH. Downloading static binary for {arch}...")
    print(f"URL: {url}")

    # Create local directory
    os.makedirs(local_ffmpeg_dir, exist_ok=True)

    # Download the archive
    archive_path = os.path.join(local_ffmpeg_dir, filename)
    try:
        print("Downloading ffmpeg (this may take a few minutes)...")
        urllib.request.urlretrieve(url, archive_path)
    except Exception as e:
        print(f"ERROR: Failed to download ffmpeg: {e}")
        print("Please install ffmpeg manually:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        sys.exit(1)

    # Extract the archive
    try:
        print("Extracting ffmpeg...")
        with tarfile.open(archive_path, "r:xz") as tar:
            # Extract only the ffmpeg binary
            for member in tar.getmembers():
                if member.name.endswith("/ffmpeg") and member.isfile():
                    # Extract to local_ffmpeg_bin
                    member.name = os.path.basename(member.name)
                    # Use filter='data' to avoid deprecation warning in Python 3.14+
                    tar.extract(member, local_ffmpeg_dir, filter="data")
                    break
    except Exception as e:
        print(f"ERROR: Failed to extract ffmpeg: {e}")
        sys.exit(1)

    # Make binary executable
    os.chmod(
        local_ffmpeg_bin,
        stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH,
    )

    # Clean up archive
    os.remove(archive_path)

    # Verify the binary works
    if not os.path.exists(local_ffmpeg_bin) or not os.access(local_ffmpeg_bin, os.X_OK):
        print("ERROR: Failed to set up ffmpeg binary.")
        sys.exit(1)

    print(f"ffmpeg successfully installed to: {local_ffmpeg_bin}")
    return local_ffmpeg_bin

