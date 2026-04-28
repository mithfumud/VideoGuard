"""Audio feature extraction and comparison utilities."""

from __future__ import annotations

import numpy as np
import librosa
from scipy.spatial.distance import cosine


def _extract_audio_feature_vector(audio_path: str) -> np.ndarray:
    """Build a deterministic audio feature vector from an audio file.

    Args:
        audio_path: Path to a WAV or audio-compatible file.

    Returns:
        A 1D feature vector combining MFCC and chroma means.
    """
    signal, sample_rate = librosa.load(audio_path, sr=None, mono=True)
    if signal.size == 0:
        return np.zeros(52, dtype=np.float32)

    mfcc = librosa.feature.mfcc(y=signal, sr=sample_rate, n_mfcc=40)
    chroma = librosa.feature.chroma_stft(y=signal, sr=sample_rate)

    mfcc_mean = np.mean(mfcc, axis=1)
    chroma_mean = np.mean(chroma, axis=1)
    feature_vector = np.concatenate([mfcc_mean, chroma_mean]).astype(np.float32)
    return feature_vector


def compute_audio_similarity(audio_path1: str | None, audio_path2: str | None) -> float:
    """Compute audio similarity score between two audio files.

    Args:
        audio_path1: First audio file path or ``None`` when unavailable.
        audio_path2: Second audio file path or ``None`` when unavailable.

    Returns:
        A similarity score between 0.0 and 1.0. If either path is ``None``,
        the function returns 0.0.
    """
    if audio_path1 is None or audio_path2 is None:
        return 0.0

    vector_1 = _extract_audio_feature_vector(audio_path1)
    vector_2 = _extract_audio_feature_vector(audio_path2)

    if np.allclose(vector_1, 0.0) or np.allclose(vector_2, 0.0):
        return 0.0

    distance = cosine(vector_1, vector_2)
    if np.isnan(distance):
        return 0.0

    similarity = 1.0 - float(distance)
    return float(np.clip(similarity, 0.0, 1.0))

