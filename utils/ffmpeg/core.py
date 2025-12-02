import subprocess
import platform
import re

from typing import Optional, Set

def get_hardware_type() -> str:
    """Detect the hardware type of the system (NVIDIA, Intel, or AMD)"""
    try:
        # First, check for NVIDIA
        nvenc = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if nvenc.returncode == 0:
            return "nvidia"

        # Based on platform, try to detect Intel or AMD
        if platform.system() == "Windows": # Windows
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True, text=True
                )
            if "Intel" in result.stdout:
                return "intel"
            elif "AMD" in result.stdout:
                return "amd"
        else: # Linux
            lspci = subprocess.run(["lspci"], capture_output=True, text=True)
            if "Intel" in lspci.stdout and ("VGA" in lspci.stdout or "3D" in lspci.stdout):
                return "intel"
            if "AMD" in lspci.stdout and ("VGA" in lspci.stdout or "3D" in lspci.stdout):
                return "amd"
    except FileNotFoundError:
        pass
    
    return ''

def get_ffmpeg_encoders() -> Set[str]:
    """Return a set of encoder names reported by `ffmpeg -encoders`"""
    try:
        p = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True, text=True, check=True
        )
    except Exception:
        return set()

    # Parse output and create set of encoders
    encoders = set()
    for line in p.stdout.splitlines():
        m = re.match(r'^\s*[A-Z\.]+\s+(\S+)\s', line)
        if m:
            encoders.add(m.group(1))
    return encoders

def detect_hw_encoder_key() -> Optional[str]:
    encs = get_ffmpeg_encoders()
    hw_type = get_hardware_type()
    if not encs:
        return None

    # NVIDIA
    if hw_type == "nvidia":
        if encs.intersection({"h264_nvenc", "hevc_nvenc", "h265_nvenc", "vp9_nvenc"}):
            return "nvenc"

    # Intel (not implemented yet)
    if hw_type == "intel" and False:
        if encs.intersection({"h264_qsv", "hevc_qsv", "h265_qsv", "vp9_qsv", "av1_qsv"}):
            return "qsv"

    # AMD
    if hw_type == "amd":
        if encs.intersection({"h264_amf", "hevc_amf", "h265_amf", "av1_amf"}):
            return "amf"

    # Fallback to VA-API (Linux)
    if hw_type == "" and platform.system() == "Linux":
        if encs.intersection({"h264_vaapi", "hevc_vaapi", "vp9_vaapi", "av1_vaapi"}):
            return "vaapi"

    return None

def build_args(encoder_key: Optional[str], ten_bit: bool, cq: int):
    """
    Hardware accelerated argument builder for ffmpeg.
    
    Args:
        encoder_key (Optional[str]): Encoder to use for video encoding
        ten_bit (bool): Should we use 10-bit encoding?
        cq (int): Constant quality, lower is better quality
    
    Returns:
        List[str]: Arguments to pass to ffmpeg
    """
    
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
            "-pix_fmt", "p010le" if ten_bit else "yuv420p"
        ]
    elif encoder_key == "qsv":
        return [
            # This uses GPU if QSV is detected
            "-c:v", "hevc_qsv",
            # Constant quality, lower is better quality
            "-q:v", str(cq),
            # Pixel format
            "-pix_fmt", "p010le" if ten_bit else "yuv420p"
        ]
    # AMF doesn't have good support for 10bit
    elif encoder_key == "amf":
        return [
            # This uses GPU if AMF is detected
            "-c:v", "hevc_amf",
            # Constant quality, lower is better quality
            "-q:v", str(cq),
        ]
    elif encoder_key == "vaapi":
        return [
            # This uses GPU if VA-API is detected
            "-c:v", "hevc_vaapi",
            "-vaapi_device", "/dev/dri/renderD128",
            # Constant quality, lower is better quality
            "-q:v", str(cq),
            # Pixel format
            "-pix_fmt", "p010le" if ten_bit else "yuv420p"
        ]
    # Fallback to libx265 if no GPU encoder is detected
    # This is actually may be a little better than other
    # encoders, but CPUs are usually slower than GPUs so
    # this is not a really good option.
    else:
        return [
            "-c:v", "libx265",
            # Very slow, best quality
            "-preset", "veryslow",
            "-crf", "24",
            "-pix_fmt", "yuv420p10le" if ten_bit else "yuv420p"
        ]

if __name__ == "__main__":
    print(f"Hardware type: {get_hardware_type()}")
    print(f"Encoder key: {detect_hw_encoder_key()}")