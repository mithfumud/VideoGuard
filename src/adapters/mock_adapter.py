"""Mock provenance adapter implementation."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.adapters.base import ProvenanceAdapter


def _registry_path() -> Path:
    """Resolve the path to the mock blockchain registry JSON file.

    Returns:
        Absolute path to ``data/registry.json`` under the project root.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    return project_root / "data" / "registry.json"


def _load_registry(registry_file: Path) -> list[dict[str, Any]]:
    """Load the registry JSON array from disk.

    Args:
        registry_file: Path to ``registry.json``.

    Returns:
        List of registry records (empty if file missing or invalid).
    """
    if not registry_file.exists():
        return []
    try:
        raw = registry_file.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_registry(registry_file: Path, records: list[dict[str, Any]]) -> None:
    """Persist the registry JSON array atomically.

    Args:
        registry_file: Path to ``registry.json``.
        records: Full list of records to write.
    """
    registry_file.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(records, indent=2, ensure_ascii=False, default=str)
    registry_file.write_text(payload + "\n", encoding="utf-8")


class MockAdapter(ProvenanceAdapter):
    """Mock IPFS/blockchain: fake CID and tx hash, storage in ``registry.json``."""

    def register_video(self, video_hash: str, owner: str, fingerprint: Any) -> dict[str, Any]:
        """Append a fake provenance record and return it.

        Args:
            video_hash: SHA256 hex (or other) unique id for the video file.
            owner: Declared owner string.
            fingerprint: Fingerprint payload (must be JSON-serializable for storage).

        Returns:
            The full stored record including ``cid``, ``tx_hash``, and ``timestamp``.
        """
        cid = "Qm" + uuid.uuid4().hex[:44]
        tx_hash = "0x" + uuid.uuid4().hex + uuid.uuid4().hex
        timestamp = datetime.now(timezone.utc).isoformat()

        record: dict[str, Any] = {
            "video_hash": video_hash,
            "owner": owner,
            "cid": cid,
            "tx_hash": tx_hash,
            "fingerprint": fingerprint,
            "timestamp": timestamp,
        }
        if isinstance(fingerprint, dict) and "source_video_path" in fingerprint:
            record["source_video_path"] = fingerprint["source_video_path"]

        registry_file = _registry_path()
        records = _load_registry(registry_file)
        records.append(record)
        _save_registry(registry_file, records)
        return record

    def lookup_video(self, video_hash: str) -> dict[str, Any] | None:
        """Find the first registry entry matching ``video_hash``.

        Args:
            video_hash: Hash to search for.

        Returns:
            Matching record dict, or ``None`` if not found.
        """
        registry_file = _registry_path()
        for entry in _load_registry(registry_file):
            if entry.get("video_hash") == video_hash:
                return entry
        return None
