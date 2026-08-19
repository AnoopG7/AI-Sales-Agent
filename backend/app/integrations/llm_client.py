"""
LLM API integration — supports Groq (hosted) and Ollama (local).
Uses a single OpenAI-compatible SDK for both providers.
"""

import structlog
from openai import AsyncOpenAI

from app.core.config import get_settings

logger = structlog.get_logger()


class LLMClient:
    """Wrapper around OpenAI-compatible chat completion APIs."""

    def __init__(self):
        settings = get_settings()

        if settings.LLM_PROVIDER == "ollama":
            self.client = AsyncOpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
            )
            self.model = settings.OLLAMA_MODEL
        else:
            self.client = AsyncOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY,
            )
            self.model = settings.GROQ_MODEL

        self.provider = settings.LLM_PROVIDER

    async def chat_completion(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_choice: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> dict:
        """Send a chat completion request with optional tool definitions.

        Returns a dict with keys: content, tool_calls, role, finish_reason.
        """
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice
            else:
                kwargs["tool_choice"] = "auto"

        response = await self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message

        tool_calls = message.tool_calls or []
        logger.info(
            "llm_completion",
            provider=self.provider,
            model=self.model,
            tokens_used=response.usage.total_tokens if response.usage else 0,
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            tool_calls=len(tool_calls),
            has_content=bool(message.content),
            finish_reason=choice.finish_reason,
        )

        return {
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "function": tc.function.name,
                    "arguments": tc.function.arguments,
                }
                for tc in tool_calls
            ],
            "role": message.role,
            "finish_reason": choice.finish_reason,
        }
