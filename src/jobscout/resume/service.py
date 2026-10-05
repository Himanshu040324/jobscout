"""Extraction orchestration: LLM call -> mapping -> grounding warnings."""

from collections.abc import Sequence

from jobscout.llm import (
    PROFILE_SYSTEM_PROMPT,
    PROJECTS_SYSTEM_PROMPT,
    RESUME_PROMPT_VERSION,
    LLMProvider,
    build_user_message,
)
from jobscout.models import Profile, ProjectsDocument, Seniority
from jobscout.resume.extraction import ExtractedProfile, ExtractedProjects
from jobscout.resume.grounding import SourceText, ungrounded_items, ungrounded_numbers
from jobscout.resume.mapper import to_profile, to_projects
from jobscout.shared import CanonicalSkills, get_logger

log = get_logger("resume.service")


def extract_profile(
    text: str,
    provider: LLMProvider,
    canon: CanonicalSkills,
    *,
    experience_level: Seniority,
    preferred_locations: Sequence[str],
    target_roles: Sequence[str],
) -> tuple[Profile, list[str]]:
    log.info("extracting profile", extra={"prompt_version": RESUME_PROMPT_VERSION})
    extracted = provider.generate_structured(
        system=PROFILE_SYSTEM_PROMPT,
        user=build_user_message(text),
        schema=ExtractedProfile,
    )
    profile, warnings = to_profile(
        extracted,
        canon,
        experience_level=experience_level,
        preferred_locations=preferred_locations,
        target_roles=target_roles,
    )

    source = SourceText(text)
    raw_skills = [skill for group in extracted.skill_groups for skill in group.skills]
    raw_skills += [tech for work in extracted.work_experience for tech in work.technologies]
    warnings += [
        f"skill/technology not found in resume text: {item!r}"
        for item in ungrounded_items(source, raw_skills)
    ]
    if ungrounded_items(source, [extracted.email]):
        warnings.append("email not found in resume text")
    return profile, warnings


def extract_projects(
    text: str, provider: LLMProvider, canon: CanonicalSkills
) -> tuple[ProjectsDocument, list[str]]:
    log.info("extracting projects", extra={"prompt_version": RESUME_PROMPT_VERSION})
    extracted = provider.generate_structured(
        system=PROJECTS_SYSTEM_PROMPT,
        user=build_user_message(text),
        schema=ExtractedProjects,
    )
    projects, warnings = to_projects(extracted, canon)

    source = SourceText(text)
    for item in extracted.projects:
        for tech in ungrounded_items(source, item.tech_stack):
            warnings.append(f"project {item.name!r}: technology not in resume text: {tech!r}")
        for label, value in (
            ("summary", item.summary),
            ("contribution", item.contribution),
            ("outcome", item.outcome or ""),
        ):
            for number in ungrounded_numbers(source, value):
                warnings.append(
                    f"project {item.name!r}: number {number!r} in {label} not in resume text"
                )
    return projects, warnings
