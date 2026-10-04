"""Typed errors. No bare exceptions anywhere in the project."""


class JobScoutError(Exception):
    """Base class for all expected, project-defined failures."""


class ConfigError(JobScoutError):
    """Raised when a config file is missing, unreadable, or fails validation."""
