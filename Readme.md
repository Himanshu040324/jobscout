# JobScout

Daily automation that fetches jobs from public ATS APIs, parses them into validated JSON,
scores them against a resume JSON, and emails a ranked digest.

See `docs/` for the phase plan and architecture notes.

## Local setup

    python -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate
    pip install -e ".[dev]"
    python -m jobscout.main --dry-run

## Quality checks

    ruff check . && ruff format --check .
    mypy src
    pytest