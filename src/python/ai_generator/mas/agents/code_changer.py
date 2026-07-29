"""
Code Changer Agent as described in 6.2.2.6.
"""

import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from config import AGENT_MODEL, AGENT_CWD
from ai_generator.mas.agents.system_prompts import CODE_CHANGER_PROMPT
from ai_generator.mas.util import add_agent_history, add_task_list, add_global_messages, add_issues, strip_json_markdown, run_with_retry
from ai_generator.mas.state import State

"""
Code Changer Agents runnable node function

Args:
    state : State - Multiagent System State

Return:
    global_messages         : Agents Global Message update
    code_changer_history    : Agents internal Dialog between invocations
"""

async def code_changer(state: State):
    # Adds the required information from the state to the system and user prompts.
    system_parts = [CODE_CHANGER_PROMPT]
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="code_changer")

    add_global_messages(state=state, input_list=prompt_parts)
    add_task_list(state=state, input_list=prompt_parts)
    add_issues(state=state, input_list=prompt_parts)

    system = "\n\n".join(system_parts)
    prompt = "\n\n".join(prompt_parts)

    # Asynchronous agent call function.
    async def run():
        result = None
        async for message in query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    model=AGENT_MODEL,
                    system_prompt=system,
                    permission_mode="bypassPermissions",
                    tools=["Read", "Edit", "Glob", "Grep", "Bash", "WebFetch"],
                    cwd=AGENT_CWD,
                ),
        ):
            # Prints all SDK messages (assistant text, tool calls, tool results, final result)
            # print("SDK MESSAGE [code_changer]:", type(message).__name__, repr(message))
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    # Agent call with appropriate prompts and repetition in the event of failure.
    json_result = await run_with_retry(run, "code_changer")
    if not json_result:
        raise RuntimeError("code_changer returned no result")

    print("RESULT [code_changer]:", repr(json_result))
    print("\n\n")

    history = json_result.get("code_changer_history", [])
    if isinstance(history, str):
        history = [history]

    return {"global_messages": [{"node": "code_changer", "message": json_result["message"]}],
            "code_changer_history": history}
