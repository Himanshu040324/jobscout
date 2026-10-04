"""Schema for profile.json (the stable part of the resume)."""

from datetime import date

from pydantic import Field

from jobscout.models.base import StrictModel
from jobscout.models.enums import Seniority


class Education(StrictModel):
    institution: str = Field(min_length=1)
    degree: str = Field(min_length=1)
    field_of_study: str | None = None
    start_year: int | None = Field(default=None, ge=1950, le=2100)
    end_year: int | None = Field(default=None, ge=1950, le=2100)
    grade: str | None = None  # kept as written on the resume (e.g. "8.4 CGPA")


class WorkExperience(StrictModel):
    company: str = Field(min_length=1)
    role: str = Field(min_length=1)
    start_date: date | None = None
    end_date: date | None = None  # None means ongoing or unknown
    summary: str = ""
    technologies: list[str] = Field(default_factory=list)


class Profile(StrictModel):
    full_name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    phone: str | None = None
    location: str = Field(min_length=1)
    education: list[Education] = Field(default_factory=list)
    skills: dict[str, list[str]] = Field(default_factory=dict)  # group -> skills
    experience_level: Seniority
    work_experience: list[WorkExperience] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    target_roles: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
