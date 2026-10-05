"""LLM-facing schemas.
All fields required (nullable where optional) for strict structured outputs.
"""

from jobscout.models import StrictModel


class ExtractedEducation(StrictModel):
    institution: str
    degree: str
    field_of_study: str | None
    start_year: int | None
    end_year: int | None
    grade: str | None


class ExtractedSkillGroup(StrictModel):
    group: str
    skills: list[str]


class ExtractedWorkExperience(StrictModel):
    company: str
    role: str
    start_date: str | None
    end_date: str | None
    summary: str
    technologies: list[str]


class ExtractedProfile(StrictModel):
    full_name: str
    email: str
    phone: str | None
    location: str
    education: list[ExtractedEducation]
    skill_groups: list[ExtractedSkillGroup]
    work_experience: list[ExtractedWorkExperience]
    certifications: list[str]
    achievements: list[str]


class ExtractedProject(StrictModel):
    name: str
    summary: str
    tech_stack: list[str]
    contribution: str
    outcome: str | None
    links: list[str]


class ExtractedProjects(StrictModel):
    projects: list[ExtractedProject]
