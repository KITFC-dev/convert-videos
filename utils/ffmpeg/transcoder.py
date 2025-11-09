import subprocess
import shlex
import shutil
from .core import detect_hw_encoder, build_args
from utils.logger import prwarn, prdebug

def transcode(
    input_path: str,
    output_path: str,
    ten_bit: bool = True,
    audio_bitrate: str = "96k",
    overwrite: bool = True,
    prefer_gpu: bool = True,
    nvenc_cq: int = 19,
    target_resolution: str = "1280x720"
):
    """
    Transcodes a video file using ffmpeg from one format to another.

    Args:
        input_path (str): Path to the input video file
        output_path (str): Path to the output video file
        ten_bit (bool): Should we use 10-bit encoding?
        audio_bitrate (str): Bitrate of the audio, "96k" is the default
        overwrite (bool): Should we overwrite output file if it exists?
        prefer_gpu (bool): Should we use the GPU for encoding?
        nvenc_cq (int): Constant quality for NVENC, lower is better quality
        target_resolution (str): Target resolution for the output video
    """
    # Check if ffmpeg is in PATH
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg not found in PATH. "
            "Please install ffmpeg from https://www.ffmpeg.org/download.html"
        )

    # Check if NVENC is available
    hw = detect_hw_encoder() if prefer_gpu else None
    if hw:
        prdebug(f"Detected hardware encoder: {hw}")
    else:
        prwarn("No hardware HEVC encoder detected, using libx265 (software).")

    # Build ffmpeg arguments based on if NVENC is available
    video_args = build_args(hw, ten_bit, nvenc_cq)

    # Build ffmpeg command
    args = [
        "ffmpeg",
        # Do we need to overwrite the output file if it exists?
        "-y" if overwrite else "-n",
        # Hide ffmpeg's info like version, configs etc.
        "-hide_banner",
        # Set the log level, setting more info than "info" is
        # not really necessary
        "-loglevel", "info",
    ]

    # Use NVENC if available, use CUDA for backend
    if hw == "nvenc":
        args += ["-hwaccel", "cuda"]

    # Set input path and target resolution, force_original_aspect_ratio
    # ensures that video wont be distorted by stretching
    args += ["-i", str(input_path),
            "-vf", f"scale={target_resolution}:force_original_aspect_ratio=decrease"]

    # Video arguments that were built earlier
    args += video_args
    # Audio arguments, "libopus" (Opus) is better at compression and has better quality,
    # but its usually not packaged with all devices, "aac" (AAC) can also be used as fallback
    args += ["-c:a", "aac", "-b:a", audio_bitrate, str(output_path)]

    # Finally, run ffmpeg
    prdebug(f"Running ffmpeg: {' '.join(shlex.quote(a) for a in args if a)}")
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1, universal_newlines=True)
    
    # Print ffmpeg's output as debug
    try:
        for line in proc.stderr:
            prdebug(line.rstrip("\r\n"))
    except KeyboardInterrupt:
        proc.terminate()
        raise
    finally:
        proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed with return code {proc.returncode}")

    prdebug(f"Done: {output_path}")
    return output_path