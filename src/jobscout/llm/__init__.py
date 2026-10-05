"""Public exports of the llm package."""

from jobscout.llm.base import LLMProvider
from jobscout.llm.openai_provider import OpenAIProvider, create_openai_provider
from jobscout.llm.prompts import (
    PROFILE_SYSTEM_PROMPT,
    PROJECTS_SYSTEM_PROMPT,
    RESUME_PROMPT_VERSION,
    build_user_message,
)

__all__ = [
    "PROFILE_SYSTEM_PROMPT",
    "PROJECTS_SYSTEM_PROMPT",
    "RESUME_PROMPT_VERSION",
    "LLMProvider",
    "OpenAIProvider",
    "build_user_message",
    "create_openai_provider",
]
