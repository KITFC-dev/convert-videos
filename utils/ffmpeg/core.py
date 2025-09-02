import subprocess
from typing import Optional

def ffmpeg_has_encoder(name: str) -> bool:
    try:
        p = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"],
                           capture_output=True, text=True, check=True)
        return name in p.stdout
    except Exception:
        return False

def detect_hw_encoder() -> Optional[str]:
    if ffmpeg_has_encoder("hevc_nvenc") or ffmpeg_has_encoder("h265_nvenc"):
        return "nvenc"
    if ffmpeg_has_encoder("hevc_qsv"):
        return "qsv"
    if ffmpeg_has_encoder("hevc_vaapi"):
        return "vaapi"
    if ffmpeg_has_encoder("hevc_amf") or ffmpeg_has_encoder("h265_amf"):
        return "amf"
    return None

def build_args(encoder_key: Optional[str], ten_bit: bool, cq: int):
    """
    NCENC Argument builder for ffmpeg.
    
    Args:
        encoder_key (Optional[str]): Encoder to use for video encoding
        ten_bit (bool): Should we use 10-bit encoding?
        cq (int): Constant quality, lower is better quality
    
    Returns:
        List[str]: Arguments to pass to ffmpeg
    """
    pix_fmt = "yuv420p10le" if ten_bit else "yuv420p"
    if encoder_key == "nvenc":
        return [
            # This uses GPU if NVENC is detected
            "-c:v", "hevc_nvenc", 
            # NVENC preset, p7 is the slowest and best quality
            "-preset", "p7",
            # Tune to prefer quality over speed
            "-tune", "hq",

            # Use variable bitrate
            "-rc:v", "vbr",
            # Constant quality, lower is better quality
            "-cq:v", str(cq),
            # Let CQ control bitrate
            "-b:v", "0",
            # Max bitrate allowed
            "-maxrate", "3M",
            # Buffer size
            "-bufsize", "6M",

            # More detail in complex areas
            "-spatial_aq", "1",
            "-aq-strength", "15",
            # This reduces bitrate in static areas
            "-temporal-aq", "1",

            # B-frames, higher is better compression but worse latency
            "-bf:v", "3",
            # What frame to use for reference
            "-b_ref_mode", "middle",
            # Enable NVENC look ahead
            "-look_ahead", "1",

            # Pixel format, prefer 10bit
            "-pix_fmt", pix_fmt
        ]
    else:
        # Fallback to libx265 if no GPU encoder is detected
        return [
            # This is actually better than NVENC, but CPUs are usually slower
            # so this is not really good option and change in size is not that big.
            # Also, I cant be bothered to wait few days for it to finish
            # compressing my 200GB video folder on my i5-13400F.
            "-c:v", "libx265",
            # Very slow, best quality
            "-preset", "veryslow",
            "-crf", "24",
            "-pix_fmt", pix_fmt
        ]
