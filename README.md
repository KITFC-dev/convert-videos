# Video Converter
## Script to convert videos to a smaller size and preserve good quality

# Requirements
1. ffmpeg needs to be installed and added to PATH.
2. Python 3.12
3. Optionally Opus for better compression of audio

# Usage
### Run the `main.py` file with these arguments:
```text
usage: main.py [-h] [-o OUTPUT] [-s SUFFIX] [-is IGNORE_SUFFIX] [-sd] [-del] [--debug] input

positional arguments:
  input                 Input folder path with videos

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output folder path for converted videos
  -s SUFFIX, --suffix SUFFIX
                        Suffix at the end of output file names
  -is IGNORE_SUFFIX, --ignore-suffix IGNORE_SUFFIX
                        Ignore files that already have this suffix
  -sd, --same-dir       Should we save to same directory as the input?
  -del, --delete-original
                        Should we delete original files after conversion?
  --debug               Enable debug logging
```