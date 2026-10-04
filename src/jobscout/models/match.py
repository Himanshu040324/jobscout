"""Schemas for scoring output. The final match_percent is computed in Python (Phase 4)."""

from pydantic import Field

from jobscout.models.base import StrictModel
from jobscout.models.enums import Recommendation


class ComponentScores(StrictModel):
    """Per-component scores returned by the LLM, each 0 to 100."""

    skills: int = Field(ge=0, le=100)
    experience: int = Field(ge=0, le=100)
    projects: int = Field(ge=0, le=100)
    education: int = Field(ge=0, le=100)
    location: int = Field(ge=0, le=100)


class MatchResult(StrictModel):
    job_key: str = Field(min_length=1)
    match_percent: int = Field(ge=0, le=100)  # computed in code, never by the LLM
    recommendation: Recommendation
    component_scores: ComponentScores
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    projects_to_highlight: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    reason: str = ""
    prompt_version: str = Field(min_length=1)
    resume_hash: str = Field(min_length=1)
