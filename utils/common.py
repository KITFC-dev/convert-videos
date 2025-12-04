import os
import time
from utils.files import VIDEO_EXTENSIONS
from functools import wraps
from typing import Optional

def to_mb(size: int) -> str:
    return f"{size / (1024**2):.2f} MB"

def mb(
    path: str, 
    ignore_suffix: Optional[str] = None,
    suffix: str = "_converted",
) -> str:
    """Return the size of a file or folder in MB."""
    size_bytes = 0
    if os.path.isfile(path):
        size_bytes = os.path.getsize(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                file_suf = os.path.splitext(file)[0]
                if file.lower().endswith(VIDEO_EXTENSIONS):
                    if file_suf.endswith(suffix):
                        if not (ignore_suffix and file_suf.endswith(ignore_suffix)):
                            file_path = os.path.join(root, file)
                            size_bytes += os.path.getsize(file_path)
    else:
        raise ValueError(f"Path not found: {path}")
    return to_mb(size_bytes)

def timed(log_func):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()

            result = func(*args, **kwargs)

            end = time.time()
            elapsed = end - start
            log_func(f"Done ({elapsed:.2f}s)")
            return result
        return wrapper
    return decorator