"""
Utility functions for ClinicGuard-AI server.

This module contains common utility functions used across the application.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Tuple
import re

logger = logging.getLogger(__name__)


def ensure_directory_exists(directory_path: str | Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Path object of the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing unsafe characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and other unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255 - len(ext)] + ext
    return sanitized


def get_audio_file_info(file_path: str | Path) -> dict:
    """
    Get information about an audio file.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Dictionary with file information (size, exists, extension)
    """
    path = Path(file_path)
    info = {
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "size_formatted": format_file_size(path.stat().st_size) if path.exists() else "0 B",
        "extension": path.suffix.lower(),
        "name": path.name
    }
    return info


def validate_environment_variables(required_vars: list[str]) -> dict[str, Optional[str]]:
    """
    Validate that required environment variables are set.
    
    Args:
        required_vars: List of environment variable names to check
        
    Returns:
        Dictionary mapping variable names to their values (None if not set)
    """
    results = {}
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        results[var] = value
        if not value:
            missing.append(var)
    
    if missing:
        logger.warning(f"Missing environment variables: {', '.join(missing)}")
    
    return results

