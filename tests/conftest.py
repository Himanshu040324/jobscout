from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import BaseModel

from jobscout.llm import LLMProvider
from jobscout.llm.base import SchemaT
from jobscout.resume import (
    ExtractedEducation,
    ExtractedProfile,
    ExtractedProject,
    ExtractedProjects,
    ExtractedSkillGroup,
)
from jobscout.shared import CanonicalSkills, load_canonical_skills

REPO_ROOT = Path(__file__).resolve().parents[1]

ProviderFactory = Callable[[str], LLMProvider]


@pytest.fixture
def repo_config_dir() -> Path:
    """The real config/ directory committed to the repo."""
    return REPO_ROOT / "config"


@pytest.fixture
def sample_resume_path() -> Path:
    return REPO_ROOT / "tests" / "fixtures" / "sample_resume.txt"


@pytest.fixture
def canon(repo_config_dir: Path) -> CanonicalSkills:
    return load_canonical_skills(repo_config_dir / "canonical_skills.yaml")


class FakeProvider:
    def __init__(self, responses: dict[type[BaseModel], BaseModel]) -> None:
        self._responses = responses

    def generate_structured(self, *, system: str, user: str, schema: type[SchemaT]) -> SchemaT:
        response = self._responses[schema]
        assert isinstance(response, schema)
        return response


@pytest.fixture
def extracted_profile() -> ExtractedProfile:
    return ExtractedProfile(
        full_name="Test Person",
        email="test.person@example.com",
        phone=None,
        location="Delhi, India",
        education=[
            ExtractedEducation(
                institution="Example Institute of Technology",
                degree="B.Tech",
                field_of_study="Mathematics and Computing",
                start_year=2023,
                end_year=2027,
                grade="CGPA: 7.5",
            )
        ],
        skill_groups=[
            ExtractedSkillGroup(group="Languages", skills=["Python", "JavaScript", "SQL"]),
            ExtractedSkillGroup(group="Frameworks", skills=["React", "Node.js"]),
            ExtractedSkillGroup(group="Tools", skills=["Git", "Docker"]),
        ],
        work_experience=[],
        certifications=[],
        achievements=[],
    )


@pytest.fixture
def extracted_projects() -> ExtractedProjects:
    return ExtractedProjects(
        projects=[
            ExtractedProject(
                name="Task Tracker",
                summary="Task tracking web app",
                tech_stack=["React", "Node.js", "PostgreSQL"],
                contribution="Built the app",
                outcome="Reduced page load time by 40%",
                links=[],
            ),
            ExtractedProject(
                name="Chat Service",
                summary="Real-time chat service",
                tech_stack=["Socket.IO", "Redis"],
                contribution="Implemented the service",
                outcome=None,
                links=[],
            ),
        ]
    )


@pytest.fixture
def fake_factory() -> Callable[[ExtractedProfile, ExtractedProjects], ProviderFactory]:
    def build(profile: ExtractedProfile, projects: ExtractedProjects) -> ProviderFactory:
        provider = FakeProvider({ExtractedProfile: profile, ExtractedProjects: projects})
        return lambda _model: provider

    return build
