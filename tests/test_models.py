from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from jobscout.models import AtsType, ComponentScores, Job, MatchResult, Recommendation


def _job(**overrides: object) -> Job:
    base: dict[str, object] = {
        "source": AtsType.GREENHOUSE,
        "company": "ExampleCo",
        "job_id": "123",
        "title": "Test Role",
        "url": "https://example.com/jobs/123",
    }
    base.update(overrides)
    return Job.model_validate(base)


def test_job_key_is_stable() -> None:
    assert _job().key == "greenhouse:ExampleCo:123"


def test_job_rejects_naive_datetime() -> None:
    with pytest.raises(ValidationError):
        _job(posted_at=datetime(2026, 1, 1, 12, 0))


def test_job_accepts_aware_datetime() -> None:
    job = _job(posted_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC))
    assert job.posted_at is not None


def test_job_rejects_inverted_experience_range() -> None:
    with pytest.raises(ValidationError, match="cannot exceed"):
        _job(min_years_experience=5, max_years_experience=2)


def test_job_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        _job(salary_guess=1)


def test_component_scores_bounds() -> None:
    with pytest.raises(ValidationError):
        ComponentScores(skills=101, experience=0, projects=0, education=0, location=0)


def test_match_percent_bounds() -> None:
    scores = ComponentScores(skills=50, experience=50, projects=50, education=50, location=50)
    with pytest.raises(ValidationError):
        MatchResult(
            job_key="k",
            match_percent=101,
            recommendation=Recommendation.MAYBE,
            component_scores=scores,
            prompt_version="v1",
            resume_hash="h",
        )
