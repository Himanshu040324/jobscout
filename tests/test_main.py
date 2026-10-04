import shutil
from pathlib import Path

import pytest

from jobscout.main import main


def test_dry_run_logs_no_stages(repo_config_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--dry-run", "--config-dir", str(repo_config_dir)])
    assert code == 0
    assert "no stages implemented yet" in capsys.readouterr().err


def test_invalid_config_exits_nonzero_with_clear_error(
    repo_config_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cfg_dir = tmp_path / "cfg"
    shutil.copytree(repo_config_dir, cfg_dir)
    (cfg_dir / "weights.yaml").write_text(
        "skills: 30\nprojects: 25\nexperience: 20\nlocation: 10\neducation: 5\n",
        encoding="utf-8",
    )
    code = main(["--dry-run", "--config-dir", str(cfg_dir)])
    assert code == 2
    assert "sum to 100" in capsys.readouterr().err


def test_limit_must_be_positive(repo_config_dir: Path) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--limit", "0", "--config-dir", str(repo_config_dir)])
    assert exc_info.value.code == 2
