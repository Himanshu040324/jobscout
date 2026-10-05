"""Typed errors. No bare exceptions anywhere in the project."""


class JobScoutError(Exception):
    """Base class for all expected, project-defined failures."""


class ConfigError(JobScoutError):
    """Raised when a config file is missing, unreadable, or fails validation."""


class LLMError(JobScoutError):
    """Raised when an LLM call fails or returns unusable output."""


class ResumeError(JobScoutError):
    """Raised when resume reading, parsing or storage fails."""
