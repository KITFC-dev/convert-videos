import os
import time
from utils.files import get_folder_size
from functools import wraps

def to_mb(size: int) -> str:
    return f"{size / (1024**2):.2f} MB"

def mb(path: str) -> str:
    """Return the size of a file or folder in MB."""
    if os.path.isfile(path):
        size_bytes = os.path.getsize(path)
    elif os.path.isdir(path):
        size_bytes = get_folder_size(path)
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