"""Base adapter interfaces for provenance backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProvenanceAdapter(ABC):
    """Abstract interface for video provenance registration and lookup."""

    @abstractmethod
    def register_video(self, video_hash: str, owner: str, fingerprint: Any) -> dict[str, Any]:
        """Register a video and return provenance metadata (e.g. CID, transaction).

        Args:
            video_hash: Unique identifier for the video (e.g. SHA256 hex).
            owner: Declared owner label or identifier.
            fingerprint: Feature fingerprint payload (structure defined by the app).

        Returns:
            A record dictionary including at least identifiers and provenance fields.
        """

    @abstractmethod
    def lookup_video(self, video_hash: str) -> dict[str, Any] | None:
        """Look up a previously registered video by hash.

        Args:
            video_hash: Unique identifier for the video.

        Returns:
            The stored record if found, otherwise ``None``.
        """
