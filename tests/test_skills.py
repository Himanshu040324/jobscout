from pathlib import Path

import pytest

from jobscout.shared import CanonicalSkills, ConfigError, load_canonical_skills


def test_aliases_collapse(canon: CanonicalSkills) -> None:
    assert canon.canonicalize("Node.js") == "nodejs"
    assert canon.canonicalize("NodeJS") == "nodejs"
    assert canon.canonicalize("node js") == "nodejs"
    assert canon.canonicalize("C++") == "cpp"


def test_unknown_skill_is_lowercased(canon: CanonicalSkills) -> None:
    assert canon.canonicalize("  Some Odd Tool ") == "some odd tool"


def test_canonicalize_all_dedupes_in_order(canon: CanonicalSkills) -> None:
    assert canon.canonicalize_all(["Node", "Python", "NodeJS", "", "python"]) == [
        "nodejs",
        "python",
    ]


def test_conflicting_alias_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "skills.yaml"
    path.write_text("canonical_skills:\n  a: [Shared]\n  b: [shared]\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="maps to both"):
        load_canonical_skills(path)


def test_canonical_name_must_be_lowercase(tmp_path: Path) -> None:
    path = tmp_path / "skills.yaml"
    path.write_text("canonical_skills:\n  NodeJS: [Node]\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="lowercase"):
        load_canonical_skills(path)
