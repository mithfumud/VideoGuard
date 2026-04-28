"""Score fusion logic for audio and video signals."""

from __future__ import annotations

from src.config import get_config


def fuse_scores(audio_score: float, video_score: float) -> tuple[float, dict[str, float]]:
    """Fuse audio and video similarity scores using configured weights.

    Args:
        audio_score: Audio similarity score in the range 0.0 to 1.0.
        video_score: Video similarity score in the range 0.0 to 1.0.

    Returns:
        A tuple containing:
        - The fused final score as a float.
        - A score breakdown dictionary with ``audio_score``, ``video_score``,
          and ``final_score``.
    """
    config = get_config()
    analysis_config = config.get("analysis", {})
    audio_weight = float(analysis_config.get("audio_weight", 0.5))
    video_weight = float(analysis_config.get("video_weight", 0.5))

    final_score = (audio_weight * float(audio_score)) + (video_weight * float(video_score))
    breakdown = {
        "audio_score": float(audio_score),
        "video_score": float(video_score),
        "final_score": float(final_score),
    }
    return float(final_score), breakdown

