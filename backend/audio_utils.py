"""
Audio streaming utilities with range request support
"""
import os
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse


def get_audio_path(verse_id: int, language: str = "ar", reciter: str = "default") -> Path:
    """
    Get the file path for audio file
    
    Args:
        verse_id: ID of the verse
        language: Language code (ar, en, te)
        reciter: Reciter name/identifier
        
    Returns:
        Path to audio file
    """
    # Base audio directory
    audio_base = Path("/home/runner/work/Deen-Hidaya/Deen-Hidaya/data/audio")
    
    # Construct path based on language and reciter
    audio_path = audio_base / language / reciter / f"{verse_id}.mp3"
    
    return audio_path


def stream_audio_file(
    file_path: Path,
    range_header: Optional[str] = None
) -> StreamingResponse:
    """
    Stream audio file with support for range requests
    
    Args:
        file_path: Path to the audio file
        range_header: HTTP Range header value
        
    Returns:
        StreamingResponse with audio data
        
    Raises:
        HTTPException: If file not found
    """
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
