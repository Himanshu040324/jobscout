from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo_config_dir() -> Path:
    """The real config/ directory committed to the repo."""
    return REPO_ROOT / "config"
