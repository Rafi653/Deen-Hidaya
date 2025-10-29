"""
Audio streaming utilities with range request support
"""
import os
import re
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse


def _sanitize_path_component(component: str, allowed_pattern: str = r'^[a-zA-Z0-9_-]+$') -> str:
    """
    Sanitize a path component to prevent path traversal attacks
    
    Args:
        component: Path component to sanitize
        allowed_pattern: Regex pattern for allowed characters
        
    Returns:
        Sanitized component
        
    Raises:
        HTTPException: If component contains invalid characters
    """
    if not re.match(allowed_pattern, component):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid path component: {component}"
        )
    return component


def get_audio_path(verse_id: int, language: str = "ar", reciter: str = "default") -> Path:
    """
    Get the file path for audio file with path traversal protection
    
    Args:
        verse_id: ID of the verse
        language: Language code (ar, en, te) - sanitized
        reciter: Reciter name/identifier - sanitized
        
    Returns:
        Path to audio file
        
    Raises:
        HTTPException: If language or reciter contains invalid characters
    """
    # Validate language code (only allow specific language codes)
    allowed_languages = ['ar', 'en', 'te']
    if language not in allowed_languages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid language code. Must be one of: {', '.join(allowed_languages)}"
        )
    
    # Sanitize reciter name (allow alphanumeric, underscore, hyphen)
    reciter = _sanitize_path_component(reciter)
    
    # Base audio directory
    audio_base = Path("/home/runner/work/Deen-Hidaya/Deen-Hidaya/data/audio")
    
    # Construct path - language and reciter are now sanitized
    audio_path = audio_base / language / reciter / f"{verse_id}.mp3"
    
    # Additional safety check: ensure the resolved path is still within audio_base
    try:
        audio_path = audio_path.resolve()
        audio_base = audio_base.resolve()
        if not str(audio_path).startswith(str(audio_base)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid audio path"
            )
    except (ValueError, RuntimeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audio path"
        )
    
    return audio_path


def stream_audio_file(
    file_path: Path,
    range_header: Optional[str] = None
) -> StreamingResponse:
    """
    Stream audio file with support for range requests
    
    SECURITY NOTE: file_path must be validated by get_audio_path() before calling this function.
    The get_audio_path() function sanitizes all user inputs and validates that the path
    stays within the allowed audio directory, preventing path traversal attacks.
    
    Args:
        file_path: Path to the audio file (must be pre-validated by get_audio_path)
        range_header: HTTP Range header value
        
    Returns:
        StreamingResponse with audio data
        
    Raises:
        HTTPException: If file not found
    """
    # NOTE: Path validation is done by get_audio_path() before calling this function
    # to prevent path traversal. See get_audio_path() for security controls.
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file not found"
        )
    
    file_size = file_path.stat().st_size
    
    # Parse range header
    start = 0
    end = file_size - 1
    
    if range_header:
        range_str = range_header.replace("bytes=", "")
        range_parts = range_str.split("-")
        
        if range_parts[0]:
            start = int(range_parts[0])
        if len(range_parts) > 1 and range_parts[1]:
            end = int(range_parts[1])
    
    # Ensure valid range
    start = max(0, start)
    end = min(file_size - 1, end)
    content_length = end - start + 1
    
    # Generator function to stream file chunks
    def iter_file():
        with open(file_path, "rb") as f:
            f.seek(start)
            remaining = content_length
            chunk_size = 8192  # 8KB chunks
            
            while remaining > 0:
                read_size = min(chunk_size, remaining)
                data = f.read(read_size)
                if not data:
                    break
                remaining -= len(data)
                yield data
    
    # Prepare headers
    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
    }
    
    status_code = 206 if range_header else 200
    
    return StreamingResponse(
        iter_file(),
        media_type="audio/mpeg",
        headers=headers,
        status_code=status_code
    )
