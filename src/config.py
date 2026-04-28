"""Configuration loader utilities for VideoGuard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def get_config() -> dict[str, Any]:
    """Load and return the application configuration from config.yaml.

    Returns:
        A dictionary containing application configuration values.

    Raises:
        FileNotFoundError: If config.yaml does not exist.
        yaml.YAMLError: If config.yaml contains invalid YAML.
    """
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    return config or {}

