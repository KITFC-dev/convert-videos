import os
import subprocess
import tempfile
import pytest
from utils.common import measure
from utils.ffmpeg.transcoder import transcode
from utils.logger import prinfo


def generate_test_video(
    path: str, 
    duration: int = 1, 
    resolution="1280x720", 
    v_bitrate="3911k", 
    a_bitrate="191k"
):
    """Create test video with audio for tests """
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    # Generate test video based on real video's parameters
    subprocess.run([
        "ffmpeg",
        "-f", "lavfi", "-i", f"color=c=black:size={resolution}:rate=30",
        "-f", "lavfi", "-i", f"sine=frequency=1000:sample_rate=48000:duration={duration}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-profile:v", "high",
        "-level", "4.1",
        "-b:v", v_bitrate,
        "-c:a", "aac",
        "-b:a", a_bitrate,
        "-ac", "2",
        "-ar", "48000",
        "-t", str(duration),
        path,
        "-y"
    ], check=True)


def run_transcode_test(input_file, prefer_gpu=True, ten_bit=False, nvenc_cq=19, audio_bitrate="96k"):
    """Helper function to run transcode function in temp dir """
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "output.mp4")

        transcode(
            input_path=input_file,
            output_path=output_path,
            ten_bit=ten_bit,
            audio_bitrate=audio_bitrate,
            prefer_gpu=prefer_gpu,
            nvenc_cq=nvenc_cq
        )

        assert os.path.exists(output_path), "Output file does not exist"
        assert os.path.getsize(output_path) > 0, "Output file is empty"

@pytest.mark.parametrize("encoder_config", [
    {"name": "nvenc", "prefer_gpu": True, "ten_bit": True, "nvenc_cq": 19},
    {"name": "x265", "prefer_gpu": False, "ten_bit": False}
])
@pytest.mark.parametrize("resolution", ["320x240", "1280x720", "1920x1080"])
@pytest.mark.parametrize("bitrate", ["500k", "5000k"])
@measure(prinfo)
def test_video_encoding(encoder_config, resolution, bitrate):
    """
    Test video transcoding with different encoder 
    configurations, resolutions, and bitrates
    """
    # Generate test video
    test_input = f"test_{encoder_config['name']}_{resolution}_{bitrate}.mp4"
    if not os.path.exists(test_input):
        generate_test_video(test_input, resolution=resolution, v_bitrate=bitrate)

    # Try to transcode the test video
    try:
        run_transcode_test(
            input_file=test_input,
            prefer_gpu=encoder_config.get("prefer_gpu", True),
            ten_bit=encoder_config.get("ten_bit", False),
            nvenc_cq=encoder_config.get("nvenc_cq", 19),
        )
    finally:
        # Delete the test video at the end
        if os.path.exists(test_input):
            os.remove(test_input)
