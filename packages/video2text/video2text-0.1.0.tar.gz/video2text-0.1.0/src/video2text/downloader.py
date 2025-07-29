import tempfile
import subprocess
import os
from typing import Optional


def download_audio_from_url(
    url          : str,
    output_dir   : Optional[str] = None,
    audio_format : str = "mp3",
    quality      : str = "bestaudio/best",
    keep_file    : bool = False
) -> str:
    """
    Downloads audio from the given URL using yt-dlp in audio-only mode.
    Args:
        url: The URL to download audio from.
        output_dir: Directory to save the file (uses temp if None).
        audio_format: Audio format to extract (default: 'mp3').
        quality: Download quality (default: 'bestaudio/best').
        keep_file: If True, do not delete the file after use.
    Returns:
        str: Path to the downloaded audio file.
    """
    if output_dir is None:
        temp_dir = tempfile.TemporaryDirectory()
        output_dir = temp_dir.name
    else:
        os.makedirs(output_dir, exist_ok=True)
        temp_dir = None

    output_template = os.path.join(output_dir, '%(title)s.%(ext)s')
    cmd = [
        'yt-dlp',
        '-f', quality,
        '--extract-audio',
        '--audio-format', audio_format,
        '--output', output_template,
        url
    ]
    subprocess.run(cmd, check=True)

    # Find the downloaded file (should be the only file in output_dir)
    files = [f for f in os.listdir(output_dir) if f.endswith(f'.{audio_format}')]
    if not files:
        raise RuntimeError(f'Audio download failed or no {audio_format} file found.')
    file_path = os.path.join(output_dir, files[0])

    if keep_file:
        return file_path

    # If using a temp dir, keep it alive by attaching to the file_path
    if temp_dir is not None:
        file_path = tempfile.NamedTemporaryFile(delete=False, dir=output_dir, suffix=f'.{audio_format}').name

    return file_path 