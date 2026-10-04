"""Schema for a parsed job posting."""

from typing import Self

from pydantic import AwareDatetime, Field, HttpUrl, model_validator

from jobscout.models.base import StrictModel
from jobscout.models.enums import AtsType, Seniority


class Job(StrictModel):
    # Deterministic fields, taken straight from the ATS payload
    source: AtsType
    company: str = Field(min_length=1)
    job_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    url: HttpUrl
    location: str | None = None
    posted_at: AwareDatetime | None = None  # timezone-aware, stored in UTC

    # LLM-extracted fields (Phase 3), validated like everything else
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_years_experience: int | None = Field(default=None, ge=0, le=60)
    max_years_experience: int | None = Field(default=None, ge=0, le=60)
    seniority: Seniority | None = None
    responsibilities: list[str] = Field(default_factory=list)
    education_requirement: str | None = None
    summary: str = ""

    @model_validator(mode="after")
    def _check_experience_range(self) -> Self:
        low, high = self.min_years_experience, self.max_years_experience
        if low is not None and high is not None and low > high:
            raise ValueError(
                f"min_years_experience ({low}) cannot exceed max_years_experience ({high})"
            )
        return self

    @property
    def key(self) -> str:
        """Stable identity used for dedupe and caching: source + company + ATS job id."""
        return f"{self.source.value}:{self.company}:{self.job_id}"
