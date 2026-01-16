"""Pytest configuration for geometry validation requirements."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


def pytest_sessionstart(session: pytest.Session) -> None:
    """Fail fast if Shapely is missing to enforce geometry validation in tests."""
    src_root = Path(__file__).resolve().parents[1] / "src"
    sys.path.insert(0, str(src_root))

    if importlib.util.find_spec("shapely") is None:
        pytest.exit(
            "Shapely is required for geometry validation tests. "
            "Install with `pip install cross-section[validation]`.",
            returncode=1,
        )
