## Architecture & Modular Boundary Rules

### Project Directory Structure


```
jobscout/
├── .github/
│   └── workflows/
│       └── daily.yml
├── config/
│   ├── preferences.yaml        # cities, roles, seniority, thresholds, email settings
│   ├── companies.yaml          # company, ats_type, board_slug
│   └── weights.yaml            # scoring weights
├── data/
│   ├── profile.json            # stable resume info (reviewed by hand)
│   ├── projects.json           # volatile projects section (reviewed by hand)
│   ├── seen_jobs.json          # dedupe state
│   └── results/                # per-run scored output, for auditing
├── src/
│   └── jobscout/
│       ├── models/             # Pydantic schemas: Profile, Project, Job, MatchResult
│       ├── resume/             # PDF -> JSON tool (manual, not part of daily run)
│       ├── sources/            # one fetcher per ATS (greenhouse.py, lever.py, ...)
│       ├── pipeline/           # dedupe, filters, job_parser, matcher, ranker
│       ├── llm/                # provider interface, prompts, structured-output calls
│       ├── delivery/           # email rendering and sending
│       ├── state/              # load/save of seen jobs, atomic writes
│       ├── shared/             # config loader, logger, event bus, errors, money/units
│       └── main.py             # orchestrates one run
├── tests/
│   ├── fixtures/               # recorded ATS and LLM responses
│   └── ...
├── docs/                       # architecture notes, phase plan, this file
├── .env.example
├── pyproject.toml
└── README.md
```

### Strict Boundary Enforcement
1. **Public Interfaces Only:** A module may only import from another module's public exports (its `__init__.py` or documented service contract). Never reach into another module's internal helpers or storage. Example: `matcher` consumes the `Job` and `Profile` models, never a fetcher's internals; `delivery` consumes ranked `MatchResult` objects, never raw LLM responses.
2. **One Fetcher per ATS:** Each source implements the same `JobSource` interface and returns raw postings. A failure in one source must not affect the others.
3. **Event-Driven Side Effects:** Use an internal event bus (or simple callback hooks) for non-blocking side effects such as metrics, logging summaries, or notifications. Avoid tight coupling between pipeline stages for these.
4. **No Unannounced Refactoring:** If an implementation requires breaking or modifying another module's boundary, stop and flag the dependency issue before proceeding.

---