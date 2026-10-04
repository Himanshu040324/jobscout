"""Loads and validates preferences.yaml, companies.yaml and weights.yaml."""

from pathlib import Path
from typing import Any, Self, TypeVar

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator

from jobscout.models import AtsType, Seniority, StrictModel
from jobscout.shared.errors import ConfigError

_ModelT = TypeVar("_ModelT", bound=BaseModel)


class ScoringWeights(StrictModel):
    """Weights for the final score. Must sum to exactly 100."""

    skills: int = Field(ge=0, le=100)
    projects: int = Field(ge=0, le=100)
    experience: int = Field(ge=0, le=100)
    location: int = Field(ge=0, le=100)
    education: int = Field(ge=0, le=100)

    @property
    def total(self) -> int:
        return self.skills + self.projects + self.experience + self.location + self.education

    @model_validator(mode="after")
    def _check_total(self) -> Self:
        if self.total != 100:
            raise ValueError(f"weights must sum to 100, got {self.total}")
        return self


class SearchPreferences(StrictModel):
    cities: list[str] = Field(min_length=1)
    roles: list[str] = Field(min_length=1)
    seniority: list[Seniority] = Field(min_length=1)
    remote_ok: bool = True
    excluded_keywords: list[str] = Field(default_factory=list)
    excluded_companies: list[str] = Field(default_factory=list)


class Thresholds(StrictModel):
    min_match_percent: int = Field(ge=0, le=100)
    max_jobs_in_digest: int = Field(ge=1)
    max_job_age_days: int = Field(ge=1)
    shortlist_size: int = Field(ge=1)


class LlmLimits(StrictModel):
    max_calls_per_run: int = Field(ge=1)
    # Money is never a float: 1 USD = 1_000_000 micro-USD.
    cost_ceiling_micro_usd: int = Field(ge=1)


class EmailSettings(StrictModel):
    subject_prefix: str = Field(min_length=1)
    smtp_host: str = Field(min_length=1)
    smtp_port: int = Field(ge=1, le=65535)
    display_timezone: str = Field(min_length=1)  # validated when the digest is built (Phase 5)


class Preferences(StrictModel):
    search: SearchPreferences
    thresholds: Thresholds
    llm: LlmLimits
    email: EmailSettings


class CompanyEntry(StrictModel):
    name: str = Field(min_length=1)
    ats: AtsType
    board_slug: str = Field(min_length=1)


class CompaniesConfig(StrictModel):
    companies: list[CompanyEntry] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_unique_boards(self) -> Self:
        seen: set[tuple[AtsType, str]] = set()
        for entry in self.companies:
            board = (entry.ats, entry.board_slug)
            if board in seen:
                raise ValueError(f"duplicate board: {entry.ats.value}/{entry.board_slug}")
            seen.add(board)
        return self


class AppConfig(StrictModel):
    preferences: Preferences
    companies: CompaniesConfig
    weights: ScoringWeights


def _read_mapping(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigError(f"config file not found: {path}") from exc
    except OSError as exc:
        raise ConfigError(f"cannot read config file {path}: {exc}") from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"{path} must contain a mapping at the top level")
    return data


def _validate(model: type[_ModelT], path: Path, data: dict[str, Any]) -> _ModelT:
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        details = "; ".join(
            f"{'.'.join(str(part) for part in err['loc']) or '<root>'}: {err['msg']}"
            for err in exc.errors()
        )
        raise ConfigError(f"invalid config {path}: {details}") from exc


def load_config(config_dir: Path) -> AppConfig:
    """Load and validate all three config files. Raises ConfigError on any problem."""
    prefs_path = config_dir / "preferences.yaml"
    companies_path = config_dir / "companies.yaml"
    weights_path = config_dir / "weights.yaml"

    return AppConfig(
        preferences=_validate(Preferences, prefs_path, _read_mapping(prefs_path)),
        companies=_validate(CompaniesConfig, companies_path, _read_mapping(companies_path)),
        weights=_validate(ScoringWeights, weights_path, _read_mapping(weights_path)),
    )
