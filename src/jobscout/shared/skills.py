"""The single canonical_skills mapping used for every skill comparison in the project."""

import re
from collections.abc import Iterable, Mapping
from pathlib import Path

import yaml
from pydantic import ValidationError

from jobscout.models import StrictModel
from jobscout.shared.errors import ConfigError

_IGNORED = re.compile(r"[\s._\-/]+")


def normalize_skill_key(skill: str) -> str:
    """Lookup key: lowercase, with whitespace, dots, hyphens, underscores, slashes removed."""
    return _IGNORED.sub("", skill.strip().lower())


class CanonicalSkills:
    def __init__(self, alias_to_canonical: Mapping[str, str]) -> None:
        self._map = dict(alias_to_canonical)

    def canonicalize(self, skill: str) -> str:
        cleaned = skill.strip()
        return self._map.get(normalize_skill_key(cleaned), cleaned.lower())

    def canonicalize_all(self, skills: Iterable[str]) -> list[str]:
        """Canonicalize, drop blanks, and de-duplicate while preserving order."""
        result: list[str] = []
        seen: set[str] = set()
        for skill in skills:
            if not skill.strip():
                continue
            canonical = self.canonicalize(skill)
            if canonical not in seen:
                seen.add(canonical)
                result.append(canonical)
        return result


class _CanonicalSkillsFile(StrictModel):
    canonical_skills: dict[str, list[str]]


def load_canonical_skills(path: Path) -> CanonicalSkills:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigError(f"config file not found: {path}") from exc
    except OSError as exc:
        raise ConfigError(f"cannot read config file {path}: {exc}") from exc

    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"{path} must contain a mapping at the top level")

    try:
        parsed = _CanonicalSkillsFile.model_validate(raw)
    except ValidationError as exc:
        details = "; ".join(
            f"{'.'.join(str(p) for p in err['loc']) or '<root>'}: {err['msg']}"
            for err in exc.errors()
        )
        raise ConfigError(f"invalid config {path}: {details}") from exc

    mapping: dict[str, str] = {}
    for canonical, aliases in parsed.canonical_skills.items():
        if canonical != canonical.strip().lower() or not canonical:
            raise ConfigError(f"{path}: canonical name {canonical!r} must be non-empty lowercase")
        for name in (canonical, *aliases):
            key = normalize_skill_key(name)
            if not key:
                continue
            existing = mapping.get(key)
            if existing is not None and existing != canonical:
                raise ConfigError(f"{path}: {name!r} maps to both {existing!r} and {canonical!r}")
            mapping[key] = canonical
    return CanonicalSkills(mapping)
