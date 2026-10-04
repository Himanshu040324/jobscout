"""Schema for projects.json (the volatile part of the resume)."""

from pydantic import Field, HttpUrl

from jobscout.models.base import StrictModel


class Project(StrictModel):
    name: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    tech_stack: list[str] = Field(default_factory=list)
    contribution: str = Field(min_length=1)
    outcome: str | None = None  # measurable outcome, only if stated in the source
    links: list[HttpUrl] = Field(default_factory=list)


class ProjectsDocument(StrictModel):
    """Top-level shape of data/projects.json."""

    projects: list[Project] = Field(default_factory=list)
