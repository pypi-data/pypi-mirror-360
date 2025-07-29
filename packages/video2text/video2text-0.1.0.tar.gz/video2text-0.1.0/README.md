# transcriber

Transcribes audio and video from a URL to text using OpenAI Whisper (local) with Python.

## Quick Setup

Run the provided setup script (macOS/Homebrew or manual ffmpeg for others):

```bash
./setup.sh
```

This will:
- Install uv (if needed)
- Create and activate a virtual environment
- Install all Python dependencies
- Install ffmpeg (macOS/Homebrew) or prompt for manual install

## Manual Setup (Alternative)

1. **Install [uv](https://github.com/astral-sh/uv):**
   ```bash
   pip install uv
   ```
2. **Create and activate a virtual environment:**
   ```bash
   uv venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies (from project root):**
   ```bash
   uv pip install -e .
   ```
4. **Install ffmpeg (required for audio extraction):**
   - **macOS (Homebrew):**
     ```bash
     brew install ffmpeg
     ```
   - **Other OS:**
     Download from [ffmpeg.org](https://ffmpeg.org/download.html) and ensure `ffmpeg` and `ffprobe` are in your PATH.

## Usage Example

```python
from transcriber.main import transcribe_url, combine_transcription

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
result = transcribe_url(url)
print(result['text'])
```

- `transcribe_url(url)` downloads and transcribes the audio from the URL.
- `transcribe_file(filename)` transcribes an audiofile. 

## Notes
- This package uses local Whisper (no API key required).
- The first run will download the Whisper model (hundreds of MB).
- ffmpeg must be installed and available in your system PATH.
