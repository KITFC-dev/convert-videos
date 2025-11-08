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

def measure(log_func, input_folder_=None):
    def decorator(func):
        @timed(log_func)
        @wraps(func)
        def wrapper(*args, **kwargs):
            input_folder = input_folder_ or (args[0] if len(args) > 0 else None)
            if input_folder:
                input_size = get_folder_size(input_folder)

            converted_files, output_folder = func(*args, **kwargs)

            if input_folder:
                output_size = get_folder_size(output_folder)
                size_reduction = input_size - output_size
                reduction_percent = ((size_reduction / input_size) * 100) if input_size > 0 else 0
                log_func(
                    f"Size reduction: {mb(input_folder)} -> "
                    f"{mb(output_folder)} ({reduction_percent:.2f}%)"
                )
            return converted_files, output_folder
        return wrapper
    return decorator
