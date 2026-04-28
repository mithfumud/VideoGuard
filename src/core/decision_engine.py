"""Decision engine for final copyright verdicts."""

from __future__ import annotations

from src.config import get_config
from src.core.audio_analyzer import compute_audio_similarity
from src.core.fusion import fuse_scores
from src.core.preprocessor import extract_audio, extract_frames
from src.core.video_analyzer import compute_video_similarity


def make_decision(final_score: float) -> dict[str, str | float]:
    """Create a verdict dictionary based on the configured threshold.

    Args:
        final_score: Combined similarity score in the range 0.0 to 1.0.

    Returns:
        A decision dictionary containing ``verdict``, ``score``, and ``message``.
    """
    config = get_config()
    threshold = float(config.get("analysis", {}).get("threshold", 0.75))
    normalized_score = float(max(0.0, min(1.0, final_score)))

    if normalized_score >= threshold:
        return {
            "verdict": "COPY",
            "score": normalized_score,
            "message": "Copyright violation detected. Matching registered content found.",
        }

    return {
        "verdict": "ORIGINAL",
        "score": normalized_score,
        "message": "No strong match found. Video appears to be original content.",
    }


def run_full_pipeline(video_path1: str, video_path2: str) -> dict[str, str | float | dict[str, str | float]]:
    """Run the full VideoGuard comparison pipeline.

    Pipeline stages:
    1. Extract audio and frames from both videos.
    2. Compute audio and video similarity sub-scores.
    3. Fuse sub-scores using config-defined weights.
    4. Produce final decision using config-defined threshold.

    Args:
        video_path1: Path to the first video.
        video_path2: Path to the second video.

    Returns:
        A complete result dictionary containing sub-scores, final score,
        and decision details.
    """
    analysis_config = get_config().get("analysis", {})
    frame_sample_rate = int(analysis_config.get("frame_sample_rate", 1))

    audio_path1 = extract_audio(video_path1)
    audio_path2 = extract_audio(video_path2)

    frames1 = extract_frames(video_path1, sample_rate=frame_sample_rate)
    frames2 = extract_frames(video_path2, sample_rate=frame_sample_rate)

    audio_score = compute_audio_similarity(audio_path1, audio_path2)
    video_score = compute_video_similarity(frames1, frames2)
    final_score, score_breakdown = fuse_scores(audio_score=audio_score, video_score=video_score)
    decision = make_decision(final_score)

    return {
        "audio_score": score_breakdown["audio_score"],
        "video_score": score_breakdown["video_score"],
        "final_score": score_breakdown["final_score"],
        "verdict": decision["verdict"],
        "message": decision["message"],
        "decision": decision,
    }

