"""Public exports of the resume package (manual tool, not part of the daily run)."""

from jobscout.resume.extraction import (
    ExtractedEducation,
    ExtractedProfile,
    ExtractedProject,
    ExtractedProjects,
    ExtractedSkillGroup,
    ExtractedWorkExperience,
)
from jobscout.resume.hashing import compute_resume_hash
from jobscout.resume.mapper import to_profile, to_projects
from jobscout.resume.reader import read_resume_text
from jobscout.resume.service import extract_profile, extract_projects
from jobscout.resume.store import (
    load_profile,
    load_projects,
    save_profile,
    save_projects,
    write_resume_hash,
)

__all__ = [
    "ExtractedEducation",
    "ExtractedProfile",
    "ExtractedProject",
    "ExtractedProjects",
    "ExtractedSkillGroup",
    "ExtractedWorkExperience",
    "compute_resume_hash",
    "extract_profile",
    "extract_projects",
    "load_profile",
    "load_projects",
    "read_resume_text",
    "save_profile",
    "save_projects",
    "to_profile",
    "to_projects",
    "write_resume_hash",
]
