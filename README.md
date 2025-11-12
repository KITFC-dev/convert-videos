# Video Converter
## Script to convert videos to a smaller size and preserve good quality

# Requirements
1. ffmpeg needs to be installed and added to PATH.
2. Python 3.12
3. Optionally Opus for better compression of audio

# Usage
### Run the `main.py` file with these arguments:
```text
Args:
    input (str): Input folder path with videos
    output (str): Output folder path for converted videos
    suffix (str): Suffix at the end of output file names
    same_dir (bool): Save to same directory as the input?
    ignore_suffix (str): Ignore files that already have this suffix
    delete_original (bool): Delete original file after conversion?
```