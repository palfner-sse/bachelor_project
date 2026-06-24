import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from python.config import MODEL_NAME
from python.mas.agents.util import add_agent_history, add_task_list, add_global_messages, add_issues
from python.mas.state import State


async def code_changer(state: State):
    system_parts = []
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="code_changer")

    add_global_messages(state=state, input_list=prompt_parts)
    add_task_list(state=state, input_list=prompt_parts)
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
                    tools=["Read", "Edit", "Glob", "Grep", "Bash"]
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    result = await run()
    if not result:
        raise RuntimeError("code_changer returned no result")

    json_result = json.loads(result)

    return {"global_messages": [{"node": "code_changer", "message": json_result["message"]}],
            "code_changer_history": json_result["code_changer_history"]}
