import os
import argparse

from typing import Optional

from utils.files import get_all_video_files, get_folder_size, get_output_path
from utils.common import mb, timed
from utils.ffmpeg.transcoder import transcode
from utils.logger import prerror, prinfo, prsuccess, prwarn

def convert_video(input: str, output: str, overwriting: bool) -> str:
    os.makedirs(os.path.dirname(output), exist_ok=True)

    transcode(
        # Input folder and output folder paths
        input_path=input,
        output_path=output,
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

    if overwriting:
        prwarn(f"Overwriting: {input}")
        os.replace(output, input)
        output = input
    return output

@timed(prinfo)
def convert_videos(input: str, suffix: str = "_converted", same_dir: bool = False, ignore_suffix: Optional[str] = None) -> list[str]:
    """
    Convert all video files in the input folder.
    Args:
        input (str): Input folder path with videos
        suffix (str): Suffix at the end of output file names
        same_dir (bool): Save to same directory as the input?
    """
    video_files = get_all_video_files(input, ignore_suffix=ignore_suffix)
    converted_files = []
    input_size = get_folder_size(input)

    for file_path in video_files:
        prinfo(f"Starting conversion for {file_path} ({mb(file_path)})")
        try:
            output_path, overwriting = get_output_path(file_path, input, suffix, same_dir)
            convert_video(file_path, output_path, overwriting)
            prsuccess(f"Converted to {output_path} ({mb(output_path)})")
            converted_files.append(output_path)
        except Exception as e:
            prerror(f"Failed to convert {file_path}: {e}")
    
    # Calculate size reduction
    output_folder = os.path.join(os.getcwd(), "converted") if not same_dir else input
    output_size = get_folder_size(output_folder)
    reduction = (((input_size - output_size) / input_size) * 100) if input_size > 0 else 0
    prinfo(f"Size reduction: {mb(input)} -> "
        f"{mb(output_folder)} ({reduction:.2f}%)")

    return converted_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to convert videos to a smaller size and preserve good quality"
    )
    parser.add_argument("input", type=str, help="Input folder path with videos")
    parser.add_argument("-s", "--suffix", type=str, default="_converted", help="Suffix at the end of output file names")
    parser.add_argument("-sd", "--same-dir", action="store_true", help="Should we save to same directory as the input?")
    parser.add_argument("-is", "--ignore-suffix", type=str, default=None, help="Ignore files that already have this suffix")
    parser.add_argument("--debug", action="store_true", default=False, help="Enable debug logging")
    args = parser.parse_args()

    import utils.logger
    utils.logger.DEBUG = args.debug

    if not os.path.exists(args.input):
        prerror(f"Input folder {args.input} does not exist")
        exit(1)

    convert_videos(args.input,
        suffix=args.suffix, 
        same_dir=args.same_dir,
        ignore_suffix=args.ignore_suffix
    )
