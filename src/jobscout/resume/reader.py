"""PDF or plain-text resume -> text. Never logs resume contents."""

from pathlib import Path

import pdfplumber

from jobscout.shared import ResumeError, get_logger

log = get_logger("resume.reader")

MIN_TEXT_CHARS = 200
_TEXT_SUFFIXES = {".txt", ".tex", ".md"}


def _read_pdf(path: Path) -> str:
    try:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
    except Exception as exc:  # pdfminer/pdfplumber raise many unrelated types
        raise ResumeError(f"cannot read PDF {path}: {type(exc).__name__}") from exc
    return "\n\n".join(pages)


def read_resume_text(path: Path) -> str:
    if not path.is_file():
        raise ResumeError(f"resume file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = _read_pdf(path)
    elif suffix in _TEXT_SUFFIXES:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ResumeError(f"cannot read {path}: {type(exc).__name__}") from exc
    else:
        raise ResumeError(f"unsupported resume format {suffix!r}; use .pdf, .txt, .tex or .md")

    text = text.strip()
    if len(text) < MIN_TEXT_CHARS:
        raise ResumeError(
            f"only {len(text)} characters extracted from {path}; "
            "the PDF may be scanned or empty. Try a plain-text copy."
        )
    log.info("resume text read", extra={"chars": len(text), "suffix": suffix})
    return text
