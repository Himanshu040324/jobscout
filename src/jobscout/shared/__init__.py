"""Public exports of the shared package."""

from jobscout.shared.config import (
    AppConfig,
    CompaniesConfig,
    CompanyEntry,
    Preferences,
    ScoringWeights,
    load_config,
)
from jobscout.shared.errors import ConfigError, JobScoutError
from jobscout.shared.logger import configure_logging, get_logger, new_run_id

__all__ = [
    "AppConfig",
    "CompaniesConfig",
    "CompanyEntry",
    "ConfigError",
    "JobScoutError",
    "Preferences",
    "ScoringWeights",
    "configure_logging",
    "get_logger",
    "load_config",
    "new_run_id",
]
