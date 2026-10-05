import json
from collections.abc import Callable
from pathlib import Path

import pytest

from jobscout.resume import (
    ExtractedProfile,
    ExtractedProjects,
    compute_resume_hash,
    load_profile,
    load_projects,
)
from jobscout.resume.cli import main
from jobscout.shared import load_config

Factory = Callable[[ExtractedProfile, ExtractedProjects], Callable[[str], object]]


def _base_args(command: str, repo_config_dir: Path, data_dir: Path, resume: Path) -> list[str]:
    return [
        command,
        "--config-dir", str(repo_config_dir),
        "--data-dir", str(data_dir),
        "--resume", str(resume),
        "--model", "fake-model",
    ]  # fmt: skip


def test_parse_writes_files_and_hash(
    repo_config_dir: Path,
    sample_resume_path: Path,
    tmp_path: Path,
    extracted_profile: ExtractedProfile,
    extracted_projects: ExtractedProjects,
    fake_factory: Factory,
) -> None:
    data_dir = tmp_path / "data"
    code = main(
        [*_base_args("parse", repo_config_dir, data_dir, sample_resume_path),
         "--experience-level", "entry"],
        provider_factory=fake_factory(extracted_profile, extracted_projects),  # type: ignore[arg-type]
    )  # fmt: skip
    assert code == 0

    profile = load_profile(data_dir)
    projects = load_projects(data_dir)
    stored = (data_dir / "resume_hash.txt").read_text(encoding="utf-8").strip()
    assert stored == compute_resume_hash(profile, projects)
    assert profile.preferred_locations == list(
        load_config(repo_config_dir).preferences.search.cities
    )
    assert [p.name for p in projects.projects] == ["Task Tracker", "Chat Service"]


def test_dry_run_writes_nothing(
    repo_config_dir: Path,
    sample_resume_path: Path,
    tmp_path: Path,
    extracted_profile: ExtractedProfile,
    extracted_projects: ExtractedProjects,
    fake_factory: Factory,
    capsys: pytest.CaptureFixture[str],
) -> None:
    data_dir = tmp_path / "data"
    code = main(
        [*_base_args("parse", repo_config_dir, data_dir, sample_resume_path),
         "--experience-level", "entry", "--dry-run"],
        provider_factory=fake_factory(extracted_profile, extracted_projects),  # type: ignore[arg-type]
    )  # fmt: skip
    assert code == 0
    assert not data_dir.exists()
    assert "Test Person" in capsys.readouterr().out


def test_projects_command_changes_only_projects_and_hash(
    repo_config_dir: Path,
    sample_resume_path: Path,
    tmp_path: Path,
    extracted_profile: ExtractedProfile,
    extracted_projects: ExtractedProjects,
    fake_factory: Factory,
) -> None:
    data_dir = tmp_path / "data"
    assert main(
        [*_base_args("parse", repo_config_dir, data_dir, sample_resume_path),
         "--experience-level", "entry"],
        provider_factory=fake_factory(extracted_profile, extracted_projects),  # type: ignore[arg-type]
    ) == 0  # fmt: skip

    profile_before = (data_dir / "profile.json").read_bytes()
    projects_before = (data_dir / "projects.json").read_bytes()
    hash_before = (data_dir / "resume_hash.txt").read_text(encoding="utf-8")

    edited = extracted_projects.model_copy(update={"projects": [extracted_projects.projects[0]]})
    assert main(
        _base_args("projects", repo_config_dir, data_dir, sample_resume_path),
        provider_factory=fake_factory(extracted_profile, edited),  # type: ignore[arg-type]
    ) == 0  # fmt: skip

    assert (data_dir / "profile.json").read_bytes() == profile_before
    assert (data_dir / "projects.json").read_bytes() != projects_before
    assert (data_dir / "resume_hash.txt").read_text(encoding="utf-8") != hash_before


def test_rehash_picks_up_manual_edits(
    repo_config_dir: Path,
    sample_resume_path: Path,
    tmp_path: Path,
    extracted_profile: ExtractedProfile,
    extracted_projects: ExtractedProjects,
    fake_factory: Factory,
) -> None:
    data_dir = tmp_path / "data"
    assert main(
        [*_base_args("parse", repo_config_dir, data_dir, sample_resume_path),
         "--experience-level", "entry"],
        provider_factory=fake_factory(extracted_profile, extracted_projects),  # type: ignore[arg-type]
    ) == 0  # fmt: skip
    hash_before = (data_dir / "resume_hash.txt").read_text(encoding="utf-8")

    path = data_dir / "profile.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["location"] = "Gurugram, India"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    assert main(["rehash", "--data-dir", str(data_dir)]) == 0
    assert (data_dir / "resume_hash.txt").read_text(encoding="utf-8") != hash_before


def test_missing_model_fails_cleanly(
    repo_config_dir: Path,
    sample_resume_path: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    args = _base_args("parse", repo_config_dir, tmp_path / "d", sample_resume_path)
    args = [a for a in args if a not in ("--model", "fake-model")]
    code = main([*args, "--experience-level", "entry"])
    assert code == 2
    assert "no model given" in capsys.readouterr().err
