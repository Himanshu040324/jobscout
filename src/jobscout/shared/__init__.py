"""Public exports of the shared package."""

from jobscout.shared.config import (
    AppConfig,
    CompaniesConfig,
    CompanyEntry,
    Preferences,
    ScoringWeights,
    load_config,
)
from jobscout.shared.errors import ConfigError, JobScoutError, LLMError, ResumeError
from jobscout.shared.fileio import atomic_write_text
from jobscout.shared.logger import configure_logging, get_logger, new_run_id
from jobscout.shared.skills import CanonicalSkills, load_canonical_skills, normalize_skill_key

__all__ = [
    "AppConfig",
    "CanonicalSkills",
    "CompaniesConfig",
    "CompanyEntry",
    "ConfigError",
    "JobScoutError",
    "LLMError",
    "Preferences",
    "ResumeError",
    "ScoringWeights",
    "atomic_write_text",
    "configure_logging",
    "get_logger",
    "load_canonical_skills",
    "load_config",
    "new_run_id",
    "normalize_skill_key",
]
