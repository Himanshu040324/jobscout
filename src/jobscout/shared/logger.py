"""Structured JSON logging with a run_id attached to every line."""

import json
import logging
import sys
import uuid
from datetime import UTC, datetime
from typing import Any, TextIO

ROOT_LOGGER_NAME = "jobscout"

# Attributes every LogRecord has; anything else came from `extra=` and is emitted as a field.
_RESERVED = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {
    "message",
    "asctime",
    "run_id",
}


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]


class _RunIdFilter(logging.Filter):
    def __init__(self, run_id: str) -> None:
        super().__init__()
        self._run_id = run_id

    def filter(self, record: logging.LogRecord) -> bool:
        record.run_id = self._run_id
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "run_id": getattr(record, "run_id", None),
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(run_id: str, level: str = "INFO", stream: TextIO | None = None) -> None:
    """(Re)configure the 'jobscout' logger. Safe to call more than once."""
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    for existing in list(logger.handlers):
        logger.removeHandler(existing)
        existing.close()

    handler = logging.StreamHandler(stream if stream is not None else sys.stderr)
    handler.addFilter(_RunIdFilter(run_id))
    handler.setFormatter(JsonFormatter())

    logger.addHandler(handler)
    logger.setLevel(level.upper())
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return a child of the 'jobscout' logger (so it inherits the handler and run_id)."""
    return logging.getLogger(f"{ROOT_LOGGER_NAME}.{name}")
