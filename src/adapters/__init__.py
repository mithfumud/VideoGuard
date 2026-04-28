"""Provenance adapter package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.config import get_config

if TYPE_CHECKING:
    from src.adapters.base import ProvenanceAdapter


def get_adapter() -> "ProvenanceAdapter":
    """Return the provenance adapter selected in ``config.yaml``.

    Reads ``provenance.backend`` and instantiates the matching implementation.

    Returns:
        A ``ProvenanceAdapter`` instance.

    Raises:
        ValueError: If ``provenance.backend`` is unknown.
    """
    config = get_config()
    backend = str(config.get("provenance", {}).get("backend", "mock")).lower()

    if backend == "mock":
        from src.adapters.mock_adapter import MockAdapter

        return MockAdapter()

    # Future: elif backend == "ipfs_ethereum": return IPFSEthereumAdapter()
    raise ValueError(f"Unknown provenance backend: {backend!r}")
