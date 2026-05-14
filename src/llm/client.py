"""Anthropic client wrapper with retry logic and token-usage logging."""

import logging
from typing import Any

import anthropic
from anthropic import APIError, APITimeoutError

logger = logging.getLogger(__name__)

# Model constants — change here, nowhere else.
FAST_MODEL = "claude-haiku-4-5-20251001"   # extraction: cheap + fast
SMART_MODEL = "claude-sonnet-4-6"           # analysis: better reasoning

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    """Return a cached Anthropic client (reads ANTHROPIC_API_KEY from env)."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # picks up key from environment
    return _client


def chat(
    messages: list[dict[str, Any]],
    *,
    system: str = "",
    model: str = FAST_MODEL,
    max_tokens: int = 1024,
    max_retries: int = 3,
) -> str:
    """Send a chat request and return the text response.

    Args:
        messages: List of {"role": ..., "content": ...} dicts.
        system: Optional system prompt string.
        model: Model ID to use (default: FAST_MODEL).
        max_tokens: Maximum tokens to generate.
        max_retries: How many times to retry on transient errors.

    Returns:
        The assistant's text response.

    Raises:
        APIError: If the request fails after all retries.
    """
    client = get_client()
    kwargs: dict[str, Any] = dict(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
    )
    if system:
        kwargs["system"] = system

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.messages.create(**kwargs)
            _log_usage(response, model)
            return response.content[0].text
        except APITimeoutError as e:
            last_error = e
            logger.warning("Claude timeout (attempt %d/%d)", attempt, max_retries)
        except APIError as e:
            # Only retry on 5xx; surface 4xx immediately.
            if e.status_code and e.status_code < 500:
                raise
            last_error = e
            logger.warning(
                "Claude API error %s (attempt %d/%d)", e.status_code, attempt, max_retries
            )

    raise APIError(f"Failed after {max_retries} retries") from last_error  # type: ignore[call-arg]


def tool_chat(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    tool_name: str,
    *,
    system: str = "",
    model: str = FAST_MODEL,
    max_tokens: int = 1024,
    max_retries: int = 3,
) -> dict[str, Any]:
    """Send a request that forces Claude to call a specific tool, return its input.

    Args:
        messages: List of {"role": ..., "content": ...} dicts.
        tools: Tool definitions to pass to the API.
        tool_name: Name of the tool Claude must call.
        system: Optional system prompt string.
        model: Model ID to use.
        max_tokens: Maximum tokens to generate.
        max_retries: How many times to retry on transient errors.

    Returns:
        The ``input`` dict from the tool_use response block.

    Raises:
        ValueError: If Claude did not call the expected tool.
        APIError: If the request fails after all retries.
    """
    client = get_client()
    kwargs: dict[str, Any] = dict(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        tools=tools,
        tool_choice={"type": "tool", "name": tool_name},
    )
    if system:
        kwargs["system"] = system

    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.messages.create(**kwargs)
            _log_usage(response, model)
            for block in response.content:
                if block.type == "tool_use" and block.name == tool_name:
                    return block.input  # type: ignore[return-value]
            raise ValueError(f"Claude did not call tool '{tool_name}'")
        except APITimeoutError as e:
            last_error = e
            logger.warning("Claude timeout (attempt %d/%d)", attempt, max_retries)
        except APIError as e:
            if e.status_code and e.status_code < 500:
                raise
            last_error = e
            logger.warning(
                "Claude API error %s (attempt %d/%d)", e.status_code, attempt, max_retries
            )

    raise APIError(f"Failed after {max_retries} retries") from last_error  # type: ignore[call-arg]


def _log_usage(response: anthropic.types.Message, model: str) -> None:
    """Log token counts for cost visibility."""
    u = response.usage
    logger.info(
        "Claude usage — model=%s input=%d output=%d",
        model,
        u.input_tokens,
        u.output_tokens,
    )
