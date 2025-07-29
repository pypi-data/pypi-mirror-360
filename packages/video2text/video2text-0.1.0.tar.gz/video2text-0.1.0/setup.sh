#!/bin/bash

# 1. Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "uv not found, installing with pip..."
    pip install uv
fi

# 2. Create and activate venv
uv venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
uv pip install -e .

# 4. Install ffmpeg
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Please install Homebrew or install ffmpeg manually."
    else
        brew install ffmpeg
    fi
else
    echo "Please install ffmpeg manually for your OS: https://ffmpeg.org/download.html"
fi

echo "Setup complete! Activate your venv with: source .venv/bin/activate" 