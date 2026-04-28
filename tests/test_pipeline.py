"""Tests for the VideoGuard analysis pipeline."""

from __future__ import annotations

import subprocess
from pathlib import Path

from src.core.decision_engine import run_full_pipeline


def _create_tiny_video_with_audio(output_path: Path) -> None:
    """Create a deterministic tiny MP4 test video with sine-wave audio.

    Args:
        output_path: Target video file path.
    """
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=blue:s=64x64:d=2:r=24",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=1000:duration=2",
        "-shortest",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        str(output_path),
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def test_identical_videos_are_copy(tmp_path: Path) -> None:
    """Verify identical tiny videos are classified as COPY."""
    video_path = tmp_path / "tiny_identical.mp4"
    _create_tiny_video_with_audio(video_path)

    result = run_full_pipeline(str(video_path), str(video_path))
    assert result["verdict"] == "COPY"


def test_pipeline_score_is_bounded(tmp_path: Path) -> None:
    """Verify final score always remains within [0.0, 1.0]."""
    video_1 = tmp_path / "tiny_1.mp4"
    video_2 = tmp_path / "tiny_2.mp4"
    _create_tiny_video_with_audio(video_1)
    _create_tiny_video_with_audio(video_2)

    result = run_full_pipeline(str(video_1), str(video_2))
    score = float(result["final_score"])
    assert 0.0 <= score <= 1.0

