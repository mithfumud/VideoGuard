"""Video feature extraction and comparison utilities."""

from __future__ import annotations

from typing import Iterable

import cv2
import imagehash
import numpy as np
from PIL import Image


def _paired_frames(frames1: list[np.ndarray], frames2: list[np.ndarray]) -> Iterable[tuple[np.ndarray, np.ndarray]]:
    """Yield deterministically paired frames from two frame lists.

    Args:
        frames1: First list of video frames.
        frames2: Second list of video frames.

    Yields:
        Tuples of corresponding frames up to the shorter length.
    """
    pair_count = min(len(frames1), len(frames2))
    for index in range(pair_count):
        yield frames1[index], frames2[index]


def _phash_similarity(frame1: np.ndarray, frame2: np.ndarray) -> float:
    """Compute perceptual hash similarity between two frames.

    Args:
        frame1: First frame in BGR format.
        frame2: Second frame in BGR format.

    Returns:
        Similarity score between 0.0 and 1.0.
    """
    image1 = Image.fromarray(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
    image2 = Image.fromarray(cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB))
    hash1 = imagehash.phash(image1)
    hash2 = imagehash.phash(image2)

    max_distance = hash1.hash.size
    distance = hash1 - hash2
    similarity = 1.0 - (distance / max_distance)
    return float(np.clip(similarity, 0.0, 1.0))


def _orb_similarity(frame1: np.ndarray, frame2: np.ndarray) -> float:
    """Compute ORB keypoint matching similarity between two frames.

    Args:
        frame1: First frame in BGR format.
        frame2: Second frame in BGR format.

    Returns:
        Similarity score between 0.0 and 1.0.
    """
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    orb = cv2.ORB_create(nfeatures=500)
    keypoints1, descriptors1 = orb.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(gray2, None)

    if descriptors1 is None or descriptors2 is None:
        return 0.0
    if len(keypoints1) == 0 or len(keypoints2) == 0:
        return 0.0

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(descriptors1, descriptors2)
    if not matches:
        return 0.0

    normalizer = max(len(keypoints1), len(keypoints2), 1)
    similarity = len(matches) / normalizer
    return float(np.clip(similarity, 0.0, 1.0))


def _color_hist_similarity(frame1: np.ndarray, frame2: np.ndarray) -> float:
    """Compute color histogram correlation similarity between two frames.

    Args:
        frame1: First frame in BGR format.
        frame2: Second frame in BGR format.

    Returns:
        Similarity score between 0.0 and 1.0.
    """
    hsv1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
    hsv2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)

    hist1 = cv2.calcHist([hsv1], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
    hist2 = cv2.calcHist([hsv2], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()

    correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    similarity = (correlation + 1.0) / 2.0
    return float(np.clip(similarity, 0.0, 1.0))


def compute_video_similarity(frames1: list[np.ndarray], frames2: list[np.ndarray]) -> float:
    """Compute video similarity score using pHash, ORB, and color histograms.

    The function compares aligned sampled frames and then combines method-level
    averages using fixed deterministic weights:
    - pHash: 0.4
    - ORB: 0.4
    - Color histogram: 0.2

    Args:
        frames1: Sampled frames from the first video.
        frames2: Sampled frames from the second video.

    Returns:
        A weighted similarity score between 0.0 and 1.0.
    """
    if not frames1 or not frames2:
        return 0.0

    phash_scores: list[float] = []
    orb_scores: list[float] = []
    color_scores: list[float] = []

    for frame1, frame2 in _paired_frames(frames1, frames2):
        phash_scores.append(_phash_similarity(frame1, frame2))
        orb_scores.append(_orb_similarity(frame1, frame2))
        color_scores.append(_color_hist_similarity(frame1, frame2))

    if not phash_scores:
        return 0.0

    phash_mean = float(np.mean(phash_scores))
    orb_mean = float(np.mean(orb_scores))
    color_mean = float(np.mean(color_scores))

    final_score = (0.4 * phash_mean) + (0.4 * orb_mean) + (0.2 * color_mean)
    return float(np.clip(final_score, 0.0, 1.0))

