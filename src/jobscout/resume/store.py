"""Reading and atomically writing profile.json, projects.json and resume_hash.txt."""

from pathlib import Path

from pydantic import ValidationError

from jobscout.models import Profile, ProjectsDocument
from jobscout.resume.hashing import compute_resume_hash
from jobscout.shared import ResumeError, atomic_write_text

PROFILE_FILE = "profile.json"
PROJECTS_FILE = "projects.json"
HASH_FILE = "resume_hash.txt"


def save_profile(data_dir: Path, profile: Profile) -> None:
    atomic_write_text(data_dir / PROFILE_FILE, profile.model_dump_json(indent=2) + "\n")


def save_projects(data_dir: Path, projects: ProjectsDocument) -> None:
    atomic_write_text(data_dir / PROJECTS_FILE, projects.model_dump_json(indent=2) + "\n")


def load_profile(data_dir: Path) -> Profile:
    path = data_dir / PROFILE_FILE
    try:
        return Profile.model_validate_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ResumeError(f"{path} not found; run the 'parse' command first") from exc
    except ValidationError as exc:
        raise ResumeError(
            f"{path} is invalid: {exc.error_count()} error(s); fix it by hand"
        ) from exc


def load_projects(data_dir: Path) -> ProjectsDocument:
    path = data_dir / PROJECTS_FILE
    try:
        return ProjectsDocument.model_validate_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ResumeError(f"{path} not found; run the 'parse' command first") from exc
    except ValidationError as exc:
        raise ResumeError(
            f"{path} is invalid: {exc.error_count()} error(s); fix it by hand"
        ) from exc


def write_resume_hash(data_dir: Path) -> str:
    """Recompute the hash from the files on disk (so hand edits are included) and store it."""
    digest = compute_resume_hash(load_profile(data_dir), load_projects(data_dir))
    atomic_write_text(data_dir / HASH_FILE, digest + "\n")
    return digest
