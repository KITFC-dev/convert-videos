import os
from typing import Optional
from utils.logger import prwarn

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv")

def get_file_size(file_path: str) -> int:
    return os.path.getsize(file_path)

def get_folder_size(folder_path: str) -> int:
    total_size = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(VIDEO_EXTENSIONS):
                file_path = os.path.join(root, file)
                total_size += get_file_size(file_path)
    return total_size

def get_all_video_files(folder_path: str, extensions=VIDEO_EXTENSIONS, ignore_suffix: Optional[str] = None) -> list[str]:
    video_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(extensions):
                if not (ignore_suffix and os.path.splitext(file)[0].endswith(ignore_suffix)):
                    video_files.append(os.path.join(root, file))
                else:
                    prwarn(f"Ignoring: {os.path.join(root, file)}")
    return video_files
