import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import MODEL_NAME
from python.mas.agents.system_prompts import CODE_CHANGE_PLANER_PROMPT
from python.mas.agents.util import add_agent_history, add_global_messages, add_task_list, \
    add_proposed_environmental_changes
from python.mas.state import State


async def code_change_planer(state: State):
    system_parts = [CODE_CHANGE_PLANER_PROMPT]
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="code_change_planer")

    add_task_list(state=state, input_list=prompt_parts)
    add_global_messages(state=state, input_list=prompt_parts)
    add_proposed_environmental_changes(state=state, input_list=prompt_parts)

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
                    tools=["Read", "Write", "Edit", "Glob", "Grep"]
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    result = await run()
    if not result:
        raise RuntimeError("code_change_planer returned no result")

    json_result = json.loads(result)

    return {"global_messages": [{"node": "code_change_planer", "message": json_result["message"]}],
            "code_change_planer_history": json_result["code_change_planer_history"]}
