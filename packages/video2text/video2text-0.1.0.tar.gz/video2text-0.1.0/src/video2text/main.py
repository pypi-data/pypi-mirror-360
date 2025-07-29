import tempfile
import os
from typing import Dict, Optional
from .downloader import download_audio_from_url
from .whisper_service import WhisperTranscriptionService


def transcribe_file(
    file_path   : str,
    model_name  : str = None,
    language    : str = None
) -> Dict:
    """
    Transcribe a local audio file using Whisper.
    Args:
        file_path: Path to the local audio file.
        model_name: Whisper model (default: 'base' or $WHISPER_MODEL).
        language: Language code hint for transcription (default: None or $LANGUAGE_HINT).
    Returns:
        dict: Transcription result in the standard JSON schema.
    """
    model_name = model_name or os.environ.get("WHISPER_MODEL", "base")
    language   = language or os.environ.get("LANGUAGE_HINT")
    transcriber = WhisperTranscriptionService(model_name=model_name)
    return transcriber.transcribe(file_path, language=language)


def transcribe_url(
    url          : str,
    audio_format : str = None,
    quality      : str = None,
    keep_file    : bool = False,
    temp_dir     : Optional[str] = None,
    model_name   : str = None,
    language     : str = None
) -> Dict:
    """
    Download audio from the given URL and transcribe it using Whisper.
    Args:
        url: The URL to download audio from.
        audio_format: Audio format to extract (default: 'mp3' or $AUDIO_FORMAT).
        quality: Download quality (default: 'bestaudio/best' or $AUDIO_QUALITY).
        keep_file: If True, do not delete the file after use.
        temp_dir: Directory for temp files (default: system temp or $TEMP_DIR).
        model_name: Whisper model (default: 'base' or $WHISPER_MODEL).
        language: Language code hint for transcription (default: None or $LANGUAGE_HINT).
    Returns:
        dict: Transcription result in the standard JSON schema.
    """
    audio_format = audio_format or os.environ.get("AUDIO_FORMAT", "mp3")
    quality      = quality or os.environ.get("AUDIO_QUALITY", "bestaudio/best")
    temp_dir     = temp_dir or os.environ.get("TEMP_DIR")
    model_name   = model_name or os.environ.get("WHISPER_MODEL", "base")
    language     = language or os.environ.get("LANGUAGE_HINT")

    if temp_dir is None:
        temp_dir_obj = tempfile.TemporaryDirectory()
        temp_dir_path = temp_dir_obj.name
    else:
        os.makedirs(temp_dir, exist_ok=True)
        temp_dir_obj = None
        temp_dir_path = temp_dir

    try:
        audio_path = download_audio_from_url(
            url,
            output_dir   = temp_dir_path,
            audio_format = audio_format,
            quality      = quality,
            keep_file    = keep_file
        )
        result = transcribe_file(
            audio_path,
            model_name=model_name,
            language=language
        )
        return result
    finally:
        if not keep_file and temp_dir_obj is not None:
            temp_dir_obj.cleanup()

