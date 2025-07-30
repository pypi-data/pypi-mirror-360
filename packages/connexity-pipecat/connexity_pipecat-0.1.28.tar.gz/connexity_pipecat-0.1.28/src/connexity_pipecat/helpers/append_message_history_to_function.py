from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.llm_service import FunctionCallParams


def append_message_history_to_function(handler, ctx: OpenAILLMContext):
    """Return a wrapper that adds live history to every function call."""

    async def _wrapper(params: FunctionCallParams):
        live_history = [m.copy() for m in ctx.messages]
        params.arguments = dict(params.arguments)
        if "messages_history" in params.arguments:
            params.arguments["messages_history"] = live_history
        return await handler(params)

    return _wrapper