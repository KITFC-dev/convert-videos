import os
import argparse
from utils.files import get_all_video_files
from utils.common import mb, measure
from utils.ffmpeg.transcoder import transcode
from utils.logger import prerror, prinfo, prsuccess, prdebug

def convert_video(file_path: str, base_folder: str):
    # Get output path
    rel_path = os.path.relpath(file_path, base_folder)
    name, ext = os.path.splitext(rel_path)
    output_path = os.path.join(os.getcwd(), "converted", f"{name}_converted{ext}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    transcode(
        # Input folder and output folder paths
        input_path=file_path,
        output_path=output_path,
        # 10bit is recommended, it has more colors and better compression,
        # the only downside is that its not compatible on all devices
        ten_bit=True,
        # Try to keep 96k unless theres music in the video, then use 128k or 256k
        audio_bitrate="96k",
        # NVENC's Constant Quantization (0-51), the smaller number the better
        # video quality is but bigger size, higher number is more compression
        nvenc_cq=28,
        # If you pick 1920x1080 it will take almost twice as long as 1280x720,
        # but conversion is almost the same size as 1280x720 for better quality.
        # Example: 1920x1080 is 2019.40 MB -> 155.57 MB (92.30%) (75.45s)
        #          1280x720  is 2019.40 MB -> 155.05 MB (92.32%) (40.06s)
        # target_resolution="1920x1080",
    )
    return output_path

@measure(prinfo)
def convert_videos(folder_path: str):
    video_files = get_all_video_files(folder_path)
    converted_files = []

    for file_path in video_files:
        prinfo(f"Starting conversion for {file_path} ({mb(file_path)})")
        try:
            output_path = convert_video(file_path, folder_path)
            prsuccess(f"Converted to {output_path} ({mb(output_path)})")
            converted_files.append(output_path)
        except Exception as e:
            prerror(f"Failed to convert {file_path}: {e}")
    return converted_files

if __name__ == "__main__":
    convert_videos(r"C:\Users\kitfc\dev\python\convertvideos\tes",
        suffix="_converted", 
        same_dir=False
    )
