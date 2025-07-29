import os
import mimetypes
import subprocess
import json
from urllib.parse import urlparse, unquote
from typing import Tuple


def get_url_extension_and_content_type(url: str) -> Tuple[str, str]:
    """
    Extract file extension and corresponding content_type from a URL
    
    Args:
        url (str): The URL to parse
        
    Returns:
        Tuple[str, str]: (extension, content_type)
            - extension: File extension (including dot, e.g., '.jpg')
            - content_type: MIME type (e.g., 'image/jpeg')
    
    Examples:
        >>> get_url_extension_and_content_type("https://example.com/image.jpg")
        ('.jpg', 'image/jpeg')
        
        >>> get_url_extension_and_content_type("https://example.com/video.mp4")
        ('.mp4', 'video/mp4')
        
        >>> get_url_extension_and_content_type("https://example.com/file")
        (None, None)
    """
    try:
        # Parse the URL
        parsed_url = urlparse(url)
        # URL decode the path part
        path = unquote(parsed_url.path)
        
        # Extract filename
        filename = os.path.basename(path)
        
        # Get file extension
        _, extension = os.path.splitext(filename)
        
        # If no extension, return None
        if not extension:
            return None, None
        
        # Guess content_type based on extension
        content_type, _ = mimetypes.guess_type(filename)
        
        return extension, content_type
        
    except Exception:
        raise ValueError(f"Failed to parse file {url}")



def get_media_duration_from_url(url: str) -> float:
    try:
        # Use ffprobe to get media duration directly from URL
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'csv=p=0',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and result.stdout.strip():
            duration = float(result.stdout.strip())
            return duration
    
    except Exception:
        return None
    
    return None


def get_media_dimensions_from_url(url: str) -> Tuple[int, int]:
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json",
            url
        ]

        output = subprocess.check_output(cmd, timeout=60).decode("utf-8")
        data = json.loads(output)
        width = data["streams"][0]["width"]
        height = data["streams"][0]["height"]
        return width, height

    except Exception:
        return None
    
    return None


if __name__ == "__main__":
    print(get_media_duration_from_url("https://replicate.delivery/xezq/vRjrsgLsBbosG1TMegwb0ly5a72YtwrejnrZdk1VeosUSpYpA/output.mp4"))
    print(get_media_duration_from_url("https://replicate.delivery/mgxm/e5159b1b-508a-4be4-b892-e1eb47850bdc/OSR_uk_000_0050_8k.wav"))

    print(get_media_dimensions("https://replicate.delivery/xezq/vRjrsgLsBbosG1TMegwb0ly5a72YtwrejnrZdk1VeosUSpYpA/output.mp4"))
    print(get_media_dimensions("https://replicate.delivery/xezq/O2UqYTphWp5TAp1d6fW5os7UCkef14irh1as0jX7eFFkzURTB/tmpxptepq5b.jpg"))

