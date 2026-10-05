"""Maps LLM-facing extraction objects into the final validated models."""

import re
from collections.abc import Sequence
from datetime import date

from pydantic import HttpUrl, TypeAdapter, ValidationError

from jobscout.models import (
    Education,
    Profile,
    Project,
    ProjectsDocument,
    Seniority,
    WorkExperience,
)
from jobscout.resume.extraction import ExtractedProfile, ExtractedProjects
from jobscout.shared import CanonicalSkills, ResumeError

_DATE = re.compile(r"^(\d{4})(?:-(\d{1,2}))?$")
_URL = TypeAdapter(HttpUrl)


def _describe(exc: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(p) for p in err['loc']) or '<root>'}: {err['msg']}" for err in exc.errors()
    )


def _parse_date(value: str | None, label: str, warnings: list[str]) -> date | None:
    """YYYY-MM -> first of that month; YYYY -> January 1 (precision is lost, by design)."""
    if value is None:
        return None
    match = _DATE.match(value.strip())
    if match is None:
        warnings.append(f"{label}: unparseable date {value!r}; stored as null")
        return None
    try:
        return date(int(match[1]), int(match[2]) if match[2] else 1, 1)
    except ValueError:
        warnings.append(f"{label}: invalid date {value!r}; stored as null")
        return None


def to_profile(
    extracted: ExtractedProfile,
    canon: CanonicalSkills,
    *,
    experience_level: Seniority,
    preferred_locations: Sequence[str],
    target_roles: Sequence[str],
) -> tuple[Profile, list[str]]:
    warnings: list[str] = []

    skills: dict[str, list[str]] = {}
    for group in extracted.skill_groups:
        name = group.group.strip().lower() or "skills"
        skills[name] = canon.canonicalize_all([*skills.get(name, []), *group.skills])
    skills = {name: items for name, items in skills.items() if items}

    work = [
        WorkExperience(
            company=item.company,
            role=item.role,
            start_date=_parse_date(item.start_date, f"work {item.company!r} start", warnings),
            end_date=_parse_date(item.end_date, f"work {item.company!r} end", warnings),
            summary=item.summary,
            technologies=canon.canonicalize_all(item.technologies),
        )
        for item in extracted.work_experience
    ]

    try:
        profile = Profile(
            full_name=extracted.full_name,
            email=extracted.email,
            phone=extracted.phone,
            location=extracted.location,
            education=[Education(**item.model_dump()) for item in extracted.education],
            skills=skills,
            experience_level=experience_level,
            work_experience=work,
            preferred_locations=list(preferred_locations),
            target_roles=list(target_roles),
            certifications=extracted.certifications,
            achievements=extracted.achievements,
        )
    except ValidationError as exc:
        raise ResumeError(f"extracted profile failed validation: {_describe(exc)}") from exc
    return profile, warnings


def to_projects(
    extracted: ExtractedProjects, canon: CanonicalSkills
) -> tuple[ProjectsDocument, list[str]]:
    warnings: list[str] = []
    projects: list[Project] = []
    for item in extracted.projects:
        links: list[HttpUrl] = []
        for link in item.links:
            try:
                links.append(_URL.validate_python(link.strip()))
            except ValidationError:
                warnings.append(f"project {item.name!r}: dropped invalid link {link!r}")
        try:
            projects.append(
                Project(
                    name=item.name,
                    summary=item.summary,
                    tech_stack=canon.canonicalize_all(item.tech_stack),
                    contribution=item.contribution,
                    outcome=item.outcome,
                    links=links,
                )
            )
        except ValidationError as exc:
            raise ResumeError(
                f"extracted project {item.name!r} failed validation: {_describe(exc)}"
            ) from exc
    return ProjectsDocument(projects=projects), warnings
