"""OpenAI implementation: structured outputs, temperature 0, bounded retry."""

import os

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageParam
from pydantic import ValidationError

from jobscout.llm.base import SchemaT
from jobscout.shared import LLMError, get_logger

log = get_logger("llm.openai")


class OpenAIProvider:
    def __init__(self, client: OpenAI, model: str, max_attempts: int = 2) -> None:
        self._client = client
        self._model = model
        self._max_attempts = max_attempts

    def generate_structured(self, *, system: str, user: str, schema: type[SchemaT]) -> SchemaT:
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        for attempt in range(1, self._max_attempts + 1):
            try:
                completion = self._client.beta.chat.completions.parse(
                    model=self._model,
                    messages=messages,
                    response_format=schema,
                    temperature=0,
                )
            except ValidationError as exc:
                # Do not log exc text: it can echo resume content.
                log.warning(
                    "structured output failed validation",
                    extra={"attempt": attempt, "error_count": exc.error_count()},
                )
                continue
            except OpenAIError as exc:
                raise LLMError(f"OpenAI request failed: {type(exc).__name__}") from exc

            parsed = completion.choices[0].message.parsed
            if parsed is not None:
                return parsed
            log.warning("model returned no parsed output", extra={"attempt": attempt})

        raise LLMError(f"no valid structured output after {self._max_attempts} attempts")


def create_openai_provider(model: str) -> OpenAIProvider:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise LLMError("OPENAI_API_KEY is not set")
    return OpenAIProvider(OpenAI(api_key=api_key), model)
