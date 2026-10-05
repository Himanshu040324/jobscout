"""Manual resume tool: python -m jobscout.resume.cli <command> ..."""

import argparse
import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from jobscout.llm import LLMProvider, create_openai_provider
from jobscout.models import Seniority
from jobscout.resume.reader import read_resume_text
from jobscout.resume.service import extract_profile, extract_projects
from jobscout.resume.store import (
    load_profile,
    save_profile,
    save_projects,
    write_resume_hash,
)
from jobscout.shared import (
    ConfigError,
    JobScoutError,
    configure_logging,
    get_logger,
    load_canonical_skills,
    load_config,
    new_run_id,
)

ProviderFactory = Callable[[str], LLMProvider]


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config-dir", type=Path, default=Path("config"))
    common.add_argument("--data-dir", type=Path, default=Path("data"))
    common.add_argument(
        "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
    )

    llm_args = argparse.ArgumentParser(add_help=False)
    llm_args.add_argument("--resume", type=Path, required=True, help=".pdf, .txt, .tex or .md")
    llm_args.add_argument("--model", default=None, help="defaults to $OPENAI_MODEL")
    llm_args.add_argument("--dry-run", action="store_true", help="print the JSON; write no files")

    parser = argparse.ArgumentParser(prog="jobscout-resume", description="Resume -> JSON tool")
    sub = parser.add_subparsers(dest="command", required=True)

    text_cmd = sub.add_parser(
        "extract-text", parents=[common], help="print extracted text (no LLM)"
    )
    text_cmd.add_argument("--resume", type=Path, required=True)

    parse_cmd = sub.add_parser(
        "parse", parents=[common, llm_args], help="regenerate profile.json and projects.json"
    )
    parse_cmd.add_argument(
        "--experience-level", choices=[s.value for s in Seniority], required=True
    )

    sub.add_parser("projects", parents=[common, llm_args], help="regenerate only projects.json")
    sub.add_parser("rehash", parents=[common], help="validate both JSON files and recompute hash")
    return parser


def _resolve_model(arg: str | None) -> str:
    model = arg or os.environ.get("OPENAI_MODEL")
    if not model:
        raise ConfigError("no model given: pass --model or set OPENAI_MODEL")
    return model


def _report(warnings: Sequence[str]) -> None:
    log = get_logger("resume.cli")
    if not warnings:
        log.info("grounding check: no warnings")
    for warning in warnings:
        log.warning("REVIEW: %s", warning)


def _cmd_parse(args: argparse.Namespace, factory: ProviderFactory) -> int:
    log = get_logger("resume.cli")
    config = load_config(args.config_dir)
    canon = load_canonical_skills(args.config_dir / "canonical_skills.yaml")
    text = read_resume_text(args.resume)
    provider = factory(_resolve_model(args.model))

    profile, profile_warnings = extract_profile(
        text,
        provider,
        canon,
        experience_level=Seniority(args.experience_level),
        preferred_locations=config.preferences.search.cities,
        target_roles=config.preferences.search.roles,
    )
    projects, project_warnings = extract_projects(text, provider, canon)
    _report([*profile_warnings, *project_warnings])

    if args.dry_run:
        print(profile.model_dump_json(indent=2))
        print(projects.model_dump_json(indent=2))
        log.info("dry run: nothing written")
        return 0

    save_profile(args.data_dir, profile)
    save_projects(args.data_dir, projects)
    digest = write_resume_hash(args.data_dir)
    log.info("resume parsed", extra={"projects": len(projects.projects), "resume_hash": digest})
    return 0


def _cmd_projects(args: argparse.Namespace, factory: ProviderFactory) -> int:
    log = get_logger("resume.cli")
    if not args.dry_run:
        load_profile(args.data_dir)  # fail before spending an LLM call
    canon = load_canonical_skills(args.config_dir / "canonical_skills.yaml")
    text = read_resume_text(args.resume)
    provider = factory(_resolve_model(args.model))

    projects, warnings = extract_projects(text, provider, canon)
    _report(warnings)

    if args.dry_run:
        print(projects.model_dump_json(indent=2))
        log.info("dry run: nothing written")
        return 0

    save_projects(args.data_dir, projects)
    digest = write_resume_hash(args.data_dir)
    log.info("projects updated", extra={"projects": len(projects.projects), "resume_hash": digest})
    return 0


def main(
    argv: Sequence[str] | None = None, *, provider_factory: ProviderFactory | None = None
) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(run_id=new_run_id(), level=args.log_level)
    log = get_logger("resume.cli")
    factory = provider_factory or create_openai_provider

    try:
        if args.command == "extract-text":
            print(read_resume_text(args.resume))
            return 0
        if args.command == "parse":
            return _cmd_parse(args, factory)
        if args.command == "projects":
            return _cmd_projects(args, factory)
        digest = write_resume_hash(args.data_dir)
        log.info("resume_hash updated", extra={"resume_hash": digest})
        return 0
    except JobScoutError as exc:
        log.error("resume command failed: %s", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
