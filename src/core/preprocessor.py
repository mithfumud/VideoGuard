"""Video and audio preprocessing helpers."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import cv2
import ffmpeg
import numpy as np


def compute_video_hash(video_path: str) -> str:
    """Compute SHA256 hex digest of the raw video file bytes.

    Args:
        video_path: Path to the video file.

    Returns:
        Lowercase hexadecimal SHA256 string.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    source_path = Path(video_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    digest = hashlib.sha256()
    with source_path.open("rb") as video_file:
        for chunk in iter(lambda: video_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_audio(video_path: str) -> str | None:
    """Extract audio from a video file into a temporary WAV file.

    Args:
        video_path: Path to the input video file.

    Returns:
        The temporary WAV file path when extraction succeeds, otherwise ``None``
        when the video has no audio stream.

    Raises:
        FileNotFoundError: If the video file does not exist.
        RuntimeError: If ffmpeg fails for reasons other than missing audio.
    """
    source_path = Path(video_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        probe_data = ffmpeg.probe(str(source_path))
    except ffmpeg.Error as exc:
        raise RuntimeError("Failed to probe video metadata.") from exc

    audio_streams = [stream for stream in probe_data.get("streams", []) if stream.get("codec_type") == "audio"]
    if not audio_streams:
        return None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        output_path = temp_file.name

    try:
        (
            ffmpeg.input(str(source_path))
            .output(output_path, ac=1, ar=22050, format="wav")
            .overwrite_output()
            .run(quiet=True)
        )
    except ffmpeg.Error as exc:
        raise RuntimeError("Audio extraction failed.") from exc

    return output_path


def extract_frames(video_path: str, sample_rate: int = 1) -> list[np.ndarray]:
    """Extract deterministic frame samples from a video.

    The function samples one frame every ``sample_rate`` seconds. With the
    default ``sample_rate=1``, it returns one frame per second.

    Args:
        video_path: Path to the input video file.
        sample_rate: Number of seconds between sampled frames.

    Returns:
        A list of frames as NumPy arrays in BGR format.

    Raises:
        FileNotFoundError: If the video file does not exist.
        ValueError: If ``sample_rate`` is less than 1.
    """
    source_path = Path(video_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if sample_rate < 1:
        raise ValueError("sample_rate must be >= 1")

    capture = cv2.VideoCapture(str(source_path))
    if not capture.isOpened():
        return []

    fps = capture.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0
    frame_interval = max(int(round(fps * sample_rate)), 1)

    sampled_frames: list[np.ndarray] = []
    frame_index = 0

    while True:
        success, frame = capture.read()
        if not success:
            break
        if frame_index % frame_interval == 0:
            sampled_frames.append(frame.copy())
        frame_index += 1

    capture.release()
    return sampled_frames

