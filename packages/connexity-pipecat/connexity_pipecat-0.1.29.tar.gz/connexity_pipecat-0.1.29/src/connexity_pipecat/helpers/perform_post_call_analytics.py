from connexity_pipecat.data.consts import PromptType
from connexity_pipecat.core.prompts import get_prompt
from connexity_pipecat.helpers.make_openai_call import make_openai_call
from connexity_pipecat.helpers.message_history_to_plain_text import message_history_to_plaintext

async def perform_post_call_analysis(
    arguments: dict,
    config: dict,
):

    prompt_str = get_prompt(
        PromptType.POST_ANALYSIS,
        config
    )

    if "messages_history" in arguments:
        arguments["messages_history"] = message_history_to_plaintext(arguments["messages_history"])
        prompt_str = prompt_str.format(**arguments)

    llm_config = config["llm"]
    return await make_openai_call(prompt_str, llm_config)
