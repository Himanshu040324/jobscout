"""resume_hash: fingerprint of both JSON files, used for cache invalidation."""

import hashlib
import json

from jobscout.models import Profile, ProjectsDocument


def compute_resume_hash(profile: Profile, projects: ProjectsDocument) -> str:
    payload = {
        "profile": profile.model_dump(mode="json"),
        "projects": projects.model_dump(mode="json"),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
