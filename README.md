# YouTube Playlist MP3 Downloader 🎵📥

A powerful Python script that downloads entire YouTube playlists and converts them to high-quality MP3 files. Perfect for creating offline music collections, podcasts, or educational content libraries.

## ✨ Features

- **🎵 Playlist Download**: Download entire YouTube playlists in one command
- **🔊 High Quality Audio**: Supports up to 320 kbps MP3 quality
- **📁 Fixed Output**: Downloads are saved to the `musique` directory at the repository root
- **⚡ Batch Processing**: Processes all videos in a playlist automatically
- **🛡️ Error Handling**: Skips problematic videos and continues downloading
- **🎛️ Configurable Bitrate**: Choose your preferred audio quality
- **📝 Clean Filenames**: Automatically sanitizes filenames for your system
- **🚀 Fast & Reliable**: Uses yt-dlp for robust downloading

## 🚀 Quick Start

### Prerequisites

Install the required dependencies:

```bash
pip install yt-dlp
```

**Note**: You'll also need `ffmpeg` installed on your system for audio conversion:

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/) or use `winget install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or equivalent for your distro

### Basic Usage

```bash
# Download a playlist (saved to musique/ directory)
python mp3.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"

# Download with custom bitrate
python mp3.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" -b 192
```

## 📋 Command Line Arguments

| Argument | Short | Description | Default | Required |
|----------|-------|-------------|---------|----------|
| `playlist_url` | - | YouTube playlist URL | - | ✅ Yes |
| `--bitrate` | `-b` | Audio bitrate in kbps | `320` | ❌ No |

## 🎵 Audio Quality Options

| Bitrate | Quality Level | File Size | Use Case |
|---------|---------------|-----------|----------|
| `128` | Standard | Small | Basic listening, storage limited |
| `192` | Good | Medium | Good balance of quality/size |
| `256` | High | Large | High-quality listening |
| `320` | Premium | Largest | Audiophile quality (default) |

## 📁 Output Structure

```
repository-root/
├── mp3.py
├── README.md
└── musique/                    # Output directory (created automatically)
    ├── Song Title 1.mp3
    ├── Song Title 2.mp3
    ├── Another Great Song.mp3
    └── ...
```

## 💡 Usage Examples

### Example 1: Basic Download
```bash
python mp3.py "https://www.youtube.com/playlist?list=PL1KFFrJTkUrO18tKrEJnXxwI9L_Bd11kU"
```

### Example 2: Lower Quality for Storage
```bash
python mp3.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" -b 128
```

### Example 3: High Quality Collection
```bash
python mp3.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" -b 320
```

## 🔧 How It Works

### Step-by-Step Process

1. **URL Validation**: Checks if the provided URL is a valid YouTube playlist
2. **Directory Setup**: Creates the output directory if it doesn't exist
3. **Playlist Analysis**: Extracts all video URLs from the playlist
4. **Download Process**: 
   - Downloads the best available audio from each video
   - Converts to MP3 format using FFmpeg
   - Applies the specified bitrate
5. **File Organization**: Saves files with clean, system-compatible names
6. **Error Handling**: Skips problematic videos and continues with the rest

### Technical Configuration

The script uses optimized settings for reliability:

```python
ydl_opts = {
    'format': 'bestaudio/best',           # Best audio quality available
    'preferredcodec': 'mp3',              # Convert to MP3
    'preferredquality': bitrate,          # Your specified bitrate
    'ignoreerrors': True,                 # Skip errors, continue downloading
    'outtmpl': '%(title)s.%(ext)s',      # Clean filename template
}
```

## 📊 Example Output

```bash
$ python mp3.py "https://www.youtube.com/playlist?list=PL1KFFrJTkUrO18tKrEJnXxwI9L_Bd11kU"

Created output directory: /path/to/repository/musique

[youtube] Extracting playlist: PL1KFFrJTkUrO18tKrEJnXxwI9L_Bd11kU
[youtube] Playlist: My Awesome Playlist
[youtube] Downloading 25 videos

[youtube] 1/25: Downloading video info
[download] Destination: /path/to/repository/musique/Amazing Song Title.mp3
[download] 100% of 4.2MiB in 00:02

[youtube] 2/25: Downloading video info
[download] Destination: /path/to/repository/musique/Another Great Track.mp3
[download] 100% of 3.8MiB in 00:02

...

Playlist download completed successfully!
```

## 🐛 Troubleshooting

### Common Issues

**"yt-dlp not found" error:**
```bash
pip install yt-dlp
```

**"ffmpeg not found" error:**
- Install ffmpeg for your operating system (see Prerequisites)
- Ensure ffmpeg is in your system PATH

**Playlist URL not working:**
- Ensure the playlist is public
- Copy the full playlist URL including the `list=` parameter
- Try using the full URL format: `https://www.youtube.com/playlist?list=PLAYLIST_ID`

**Some videos skip/fail:**
- This is normal for private, deleted, or restricted videos
- The script will automatically skip these and continue

**Permission errors:**
- Ensure you have write permissions to the repository directory
- Try running with administrator/sudo privileges if needed

### Getting Playlist URLs

1. Go to the YouTube playlist
2. Copy the URL from your browser's address bar
3. The URL should look like: `https://www.youtube.com/playlist?list=PL1KFFrJTkUrO...`

## ⚡ Performance Tips

- **Internet Speed**: Download speed depends on your internet connection
- **Bitrate Choice**: Lower bitrates download faster and use less storage
- **Batch Size**: The script processes videos sequentially for stability
- **Storage Space**: Ensure you have enough disk space (320kbps ≈ 2.5MB per minute)

## 🔒 Legal Considerations

- Only download content you have permission to download
- Respect YouTube's Terms of Service
- Consider the copyright status of the content
- Use for personal, educational, or fair use purposes

## 🆘 Support & Help

### Command Help
```bash
python mp3.py --help
```

### Common Solutions

**Slow downloads**: Check your internet connection and try a lower bitrate

**Audio quality issues**: Ensure you're using an appropriate bitrate for your needs

**File naming issues**: The script automatically handles special characters in titles

## 🔄 Updates & Maintenance

Keep your tools updated for best performance:

```bash
pip install --upgrade yt-dlp
```

## 📚 Advanced Usage

### Batch Processing Multiple Playlists

Create a batch file with multiple commands:

```bash
#!/bin/bash
python mp3.py "PLAYLIST_1"
python mp3.py "PLAYLIST_2"
python mp3.py "PLAYLIST_3"
```

All playlists will be downloaded to the `musique/` directory.

### Integration with Other Tools

The downloaded MP3s work with:
- Music players (iTunes, VLC, etc.)
- Mobile devices
- Streaming servers (Plex, Jellyfin)
- Audio editing software

---

**Happy downloading! 🎶✨**

*Note: Always respect copyright laws and YouTube's Terms of Service when downloading content.*
