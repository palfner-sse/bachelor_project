import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import AGENT_MODEL, AGENT_CWD
from python.ai_generator.mas.agents.system_prompts import CODE_CHANGE_PLANER_PROMPT
from python.ai_generator.mas.agents.util import add_agent_history, add_global_messages, add_task_list, \
    add_proposed_environmental_changes, strip_json_markdown, run_with_retry
from python.ai_generator.mas.state import State


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
                    model=AGENT_MODEL,
                    system_prompt=system,
                    permission_mode="bypassPermissions",
                    tools=["Read", "Write", "Edit", "Glob", "Grep", "WebFetch"],
                    cwd=AGENT_CWD,
                ),
        ):
            print("SDK MESSAGE [code_change_planer]:", type(message).__name__, repr(message))
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    result = await run_with_retry(run, "code_change_planer")
    if not result:
        raise RuntimeError("code_change_planer returned no result")

    print("RAW RESULT [code_change_planer]:", repr(result))
    json_result = json.loads(strip_json_markdown(result))

    return {"global_messages": [{"node": "code_change_planer", "message": json_result["message"]}],
            "code_change_planer_history": json_result["code_change_planer_history"]}
