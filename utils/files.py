import os
from typing import Optional
from utils.logger import prwarn

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv")

def get_file_size(file_path: str) -> int:
    return os.path.getsize(file_path)

def get_folder_size(folder_path: str, ignore_suffix: Optional[str] = None) -> int:
    total_size = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(VIDEO_EXTENSIONS):
                if not (ignore_suffix and os.path.splitext(file)[0].endswith(ignore_suffix)):
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

def get_output_path(
    file_path: str, 
    input_folder: str, 
    output_folder: Optional[str] = None, 
    suffix: str = "", 
    same_dir: bool = False
) -> tuple[str, bool]:
    # Get relative path of the file 
    # (rel path will be /sub/file.mp4 if input is .../input_folder/sub/file.mp4)
    rel_path = os.path.relpath(file_path, input_folder)
    name, ext = os.path.splitext(rel_path)
    overwriting = True if suffix == "" and same_dir else False

    # Output path will prioritize same_dir, then output_folder,
    # if nothing provided, will use converted folder in cwd
    if same_dir:
        output_path = os.path.join(input_folder, 
        f"{name}{'.' if overwriting else ''}{suffix}{ext}")
    else:
        if output_folder:
            output_path = os.path.join(output_folder, rel_path)
        else:
            output_path = os.path.join(os.getcwd(),
             "converted", 
             f"{name}{suffix}{ext}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    return output_path, overwriting
