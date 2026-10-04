"""Shared base class for every Pydantic model in the project."""

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Immutable model that rejects unknown fields.

    Rejecting unknown fields means a typo in a YAML file, or an LLM inventing an extra
    key, fails loudly instead of being silently ignored.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)
