from datetime import date
from pathlib import Path

import pytest

from jobscout.models import Seniority
from jobscout.resume import (
    ExtractedProfile,
    ExtractedProject,
    ExtractedProjects,
    compute_resume_hash,
    read_resume_text,
    to_profile,
    to_projects,
)
from jobscout.resume.grounding import SourceText, ungrounded_items, ungrounded_numbers
from jobscout.shared import CanonicalSkills, ResumeError, atomic_write_text


def test_grounding_flags_missing_skill_and_number(sample_resume_path: Path) -> None:
    source = SourceText(sample_resume_path.read_text(encoding="utf-8"))
    assert ungrounded_items(source, ["Python", "Node.js", "Socket.IO", "Rust"]) == ["Rust"]
    assert ungrounded_numbers(source, "Reduced load time by 40% and cost by 75%") == ["75"]


def test_grounding_short_skill_needs_standalone_token() -> None:
    source = SourceText("Experienced in JavaScript and Python")
    assert ungrounded_items(source, ["C"]) == ["C"]


def test_mapper_canonicalizes_and_merges_groups(
    extracted_profile: ExtractedProfile, canon: CanonicalSkills
) -> None:
    profile, warnings = to_profile(
        extracted_profile,
        canon,
        experience_level=Seniority.ENTRY,
        preferred_locations=["Delhi"],
        target_roles=["SDE"],
    )
    assert profile.skills["frameworks"] == ["react", "nodejs"]
    assert profile.experience_level is Seniority.ENTRY
    assert warnings == []


def test_mapper_parses_dates_and_warns_on_bad_ones(
    extracted_profile: ExtractedProfile, canon: CanonicalSkills
) -> None:
    from jobscout.resume import ExtractedWorkExperience

    work = ExtractedWorkExperience(
        company="Example Corp",
        role="Intern",
        start_date="2025-06",
        end_date="sometime",
        summary="",
        technologies=["Node"],
    )
    profile, warnings = to_profile(
        extracted_profile.model_copy(update={"work_experience": [work]}),
        canon,
        experience_level=Seniority.INTERN,
        preferred_locations=[],
        target_roles=[],
    )
    assert profile.work_experience[0].start_date == date(2025, 6, 1)
    assert profile.work_experience[0].end_date is None
    assert profile.work_experience[0].technologies == ["nodejs"]
    assert any("unparseable date" in w for w in warnings)


def test_project_links_validated(canon: CanonicalSkills) -> None:
    extracted = ExtractedProjects(
        projects=[
            ExtractedProject(
                name="P",
                summary="s",
                tech_stack=[],
                contribution="c",
                outcome=None,
                links=["https://github.com/example/repo", "github.com/no-scheme"],
            )
        ]
    )
    projects, warnings = to_projects(extracted, canon)
    assert len(projects.projects[0].links) == 1
    assert any("invalid link" in w for w in warnings)


def test_hash_is_deterministic_and_sensitive(
    extracted_profile: ExtractedProfile,
    extracted_projects: ExtractedProjects,
    canon: CanonicalSkills,
) -> None:
    profile, _ = to_profile(
        extracted_profile,
        canon,
        experience_level=Seniority.ENTRY,
        preferred_locations=[],
        target_roles=[],
    )
    projects_a, _ = to_projects(extracted_projects, canon)
    changed = extracted_projects.model_copy(update={"projects": [extracted_projects.projects[0]]})
    projects_b, _ = to_projects(changed, canon)

    assert compute_resume_hash(profile, projects_a) == compute_resume_hash(profile, projects_a)
    assert compute_resume_hash(profile, projects_a) != compute_resume_hash(profile, projects_b)


def test_atomic_write_leaves_no_temp_files(tmp_path: Path) -> None:
    target = tmp_path / "out.json"
    atomic_write_text(target, "{}\n")
    atomic_write_text(target, '{"a": 1}\n')
    assert target.read_text(encoding="utf-8") == '{"a": 1}\n'
    assert [p.name for p in tmp_path.iterdir()] == ["out.json"]


def test_reader_reads_text_and_rejects_short_or_unknown(
    sample_resume_path: Path, tmp_path: Path
) -> None:
    assert "Task Tracker" in read_resume_text(sample_resume_path)

    short = tmp_path / "short.txt"
    short.write_text("too short", encoding="utf-8")
    with pytest.raises(ResumeError, match="characters extracted"):
        read_resume_text(short)

    odd = tmp_path / "resume.docx"
    odd.write_text("x", encoding="utf-8")
    with pytest.raises(ResumeError, match="unsupported"):
        read_resume_text(odd)
