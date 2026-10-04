import shutil
from pathlib import Path

import pytest

from jobscout.shared import ConfigError, load_config


def _copy_config(src: Path, dst: Path) -> Path:
    shutil.copytree(src, dst)
    return dst


def test_repo_config_loads(repo_config_dir: Path) -> None:
    config = load_config(repo_config_dir)
    assert config.weights.total == 100


def test_weights_not_summing_to_100_fail_fast(repo_config_dir: Path, tmp_path: Path) -> None:
    cfg_dir = _copy_config(repo_config_dir, tmp_path / "cfg")
    (cfg_dir / "weights.yaml").write_text(
        "skills: 30\nprojects: 25\nexperience: 20\nlocation: 10\neducation: 5\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="sum to 100, got 90"):
        load_config(cfg_dir)


def test_missing_file_is_reported(repo_config_dir: Path, tmp_path: Path) -> None:
    cfg_dir = _copy_config(repo_config_dir, tmp_path / "cfg")
    (cfg_dir / "companies.yaml").unlink()
    with pytest.raises(ConfigError, match="not found"):
        load_config(cfg_dir)


def test_unknown_key_is_rejected(repo_config_dir: Path, tmp_path: Path) -> None:
    cfg_dir = _copy_config(repo_config_dir, tmp_path / "cfg")
    (cfg_dir / "weights.yaml").write_text(
        "skills: 40\nprojects: 25\nexperience: 20\nlocation: 10\neducation: 5\nbonus: 1\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="bonus"):
        load_config(cfg_dir)


def test_duplicate_company_board_is_rejected(repo_config_dir: Path, tmp_path: Path) -> None:
    cfg_dir = _copy_config(repo_config_dir, tmp_path / "cfg")
    (cfg_dir / "companies.yaml").write_text(
        "companies:\n"
        "  - {name: A, ats: greenhouse, board_slug: same}\n"
        "  - {name: B, ats: greenhouse, board_slug: same}\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="duplicate board"):
        load_config(cfg_dir)


def test_invalid_yaml_is_reported(repo_config_dir: Path, tmp_path: Path) -> None:
    cfg_dir = _copy_config(repo_config_dir, tmp_path / "cfg")
    (cfg_dir / "weights.yaml").write_text("skills: [unclosed\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="invalid YAML"):
        load_config(cfg_dir)
