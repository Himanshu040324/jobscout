"""Provider-agnostic interface for structured LLM calls."""

from typing import Protocol, TypeVar

from pydantic import BaseModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class LLMProvider(Protocol):
    def generate_structured(self, *, system: str, user: str, schema: type[SchemaT]) -> SchemaT:
        """Return a validated instance of `schema`. Raises LLMError on failure."""
        ...
