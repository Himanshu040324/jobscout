"""Entry point: orchestrates one run. Phase 0 only loads config and logs."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from jobscout.shared import ConfigError, configure_logging, get_logger, load_config, new_run_id


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected an integer, got {value!r}") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jobscout", description="Daily job-matching digest")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print/write the digest locally; send no email and commit no state",
    )
    parser.add_argument(
        "--limit",
        type=_positive_int,
        default=None,
        help="process at most N jobs (for cheap test runs)",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path("config"),
        help="directory containing preferences.yaml, companies.yaml, weights.yaml",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    run_id = new_run_id()
    configure_logging(run_id=run_id, level=args.log_level)
    # Not __name__: when run via `python -m`, __name__ is "__main__", outside the 'jobscout' tree.
    log = get_logger("main")

    try:
        config = load_config(args.config_dir)
    except ConfigError as exc:
        log.error("configuration invalid: %s", exc)
        return 2

    log.info(
        "run started",
        extra={
            "dry_run": args.dry_run,
            "limit": args.limit,
            "companies_configured": len(config.companies.companies),
        },
    )
    log.info("no stages implemented yet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
