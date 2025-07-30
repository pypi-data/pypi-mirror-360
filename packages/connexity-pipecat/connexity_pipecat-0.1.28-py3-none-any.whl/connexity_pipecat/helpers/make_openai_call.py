import openai
from openai import AsyncOpenAI
from typing import Literal

from connexity_pipecat.core.config import get_config

from connexity_pipecat.data.consts import OPENAI_API_KEY

# Re‑use a single AsyncOpenAI client across calls to avoid the
# connection‑set‑up overhead on every invocation.
_async_client: AsyncOpenAI = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def make_openai_call(
    system_prompt: str,
    query: str | None = None,
    type: Literal["main", "utils"] = "utils",
    *,
    llm_config: dict,
    stream: bool = False,
) -> str:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    model = llm_config[type]["model"]
    message_history = [
        {"role": "system", "content": system_prompt},
    ]

    if query:
        message_history.append({"role": "user", "content": query})

    # Use the caller‑supplied client if given; otherwise fall back to the
    # singleton created at import time.
    client = client or _async_client

    if stream:
        parts: list[str] = []
        async for chunk in client.chat.completions.create(
            model=model,
            messages=message_history,
            stream=True,
        ):
            parts.append(chunk.choices[0].delta.content or "")
        return "".join(parts).strip()

    response = await client.chat.completions.create(
        model=model,
        messages=message_history,
        timeout=20,  # small client‑side timeout to fail fast
    )
    return response.choices[0].message.content.strip()