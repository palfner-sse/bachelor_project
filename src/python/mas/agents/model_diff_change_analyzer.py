import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import MODEL_NAME
from python.mas.agents.system_prompts import MODEL_DIFF_CHANGE_ANALYZER_PROMPT, BUML_DOKUMENTATION
from python.mas.agents.util import add_agent_history, add_model_diff, add_task_list, add_models, add_global_messages, \
    add_proposed_environmental_changes, add_issues
from python.mas.state import State


async def model_diff_change_analyzer(state: State):
    system_parts = [MODEL_DIFF_CHANGE_ANALYZER_PROMPT, BUML_DOKUMENTATION]
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="model_diff_change_analyzer")

    add_task_list(state=state, input_list=prompt_parts)
    add_global_messages(state=state, input_list=prompt_parts)
    add_model_diff(state=state, input_list=prompt_parts)
    add_models(state=state, input_list=prompt_parts)
    add_proposed_environmental_changes(state=state, input_list=prompt_parts)
    add_issues(state=state, input_list=prompt_parts)

    system = "\n\n".join(system_parts)
    prompt = "\n\n".join(prompt_parts)

    async def run():
        result = None
        async for message in query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    model=MODEL_NAME,
                    system_prompt=system,
                    permission_mode="dontAsk",
                    tools=["WebFetch"],
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    result = await run()
    if not result:
        raise RuntimeError("model_diff_change_analyzer returned no result")

    json_result = json.loads(result)

    return {"global_messages": [{"node": "model_diff_change_analyzer", "message": json_result["message"]}],
            "proposed_environmental_changes": [{"proposed_change": c["proposed_change"], "source": c["source"],
                                                "reasoning": c["reasoning"]}
                                               for c in json_result["proposed_environmental_changes"]],
            "model_diff_change_analyzer_history": json_result["model_diff_change_analyzer_history"]}
