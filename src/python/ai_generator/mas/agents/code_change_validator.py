"""
Code Change Validator Agent as described in 6.2.2.7.
"""

import json

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from config import AGENT_MODEL, ROUTING_MODEL, AGENT_CWD
from ai_generator.mas.agents.system_prompts import BUML_DOKUMENTATION, CODE_CHANGE_VALIDATOR_PROMPT, \
    CODE_CHANGE_VALIDATOR_PATH_PROMPT
from ai_generator.mas.util import add_agent_history, add_task_list, add_global_messages, add_model_diff, add_models, \
    add_issues, strip_json_markdown, run_with_retry
from ai_generator.mas.state import State

"""
Code Change Validator Agents runnable node function

Args:
    state : State - Multiagent System State

Return:
    global_messages                  : Agents Global Message update
    issues                           : Agents proposed issues in the work proposed by the Code Changer Agent
    code_change_validator_history    : Agents internal Dialog between invocations
"""

async def code_change_validator(state: State):
    # Adds the required information from the state to the system and user prompts.
    system_parts = [CODE_CHANGE_VALIDATOR_PROMPT, BUML_DOKUMENTATION]
    prompt_parts = []

    add_agent_history(state=state, input_list=system_parts, agent_name="code_change_validator")

    add_task_list(state=state, input_list=prompt_parts)
    add_global_messages(state=state, input_list=prompt_parts)
    add_model_diff(state=state, input_list=prompt_parts)
    add_models(state=state, input_list=prompt_parts)
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
            # print("SDK MESSAGE [code_change_validator]:", type(message).__name__, repr(message))
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    # Agent call with appropriate prompts and repetition in the event of failure.
    json_result = await run_with_retry(run, "code_change_validator")
    if not json_result:
        raise RuntimeError("code_change_validator returned no result")

    print("RESULT [code_change_validator]:", repr(json_result))
    print("\n\n")

    history = json_result.get("code_change_validator_history", [])
    if isinstance(history, str):
        history = [history]

    return {"global_messages": [{"node": "code_change_validator", "message": json_result["message"]}],
            "issues": [{"issue": i["issue"], "source": i["source"], "reasoning": i["reasoning"]}
                       for i in json_result.get("issues", [])] if isinstance(json_result.get("issues"), list) else [],
            "code_change_validator_history": history}


"""
Routing function of the Code Change Validator Agent, which determines whether the previous agent must
revise its work or whether routing can return to the orchestrator because the previous work has been validated.

Args:
    state : State - Multiagent System State

Return:
    str : Next node name to route to
"""
async def code_change_validator_routing(state: State):
    # Adds the required information from the state to the system and user prompts.
    system_parts = [CODE_CHANGE_VALIDATOR_PATH_PROMPT]
    prompt_parts = []

    add_global_messages(state=state, input_list=prompt_parts)
    add_issues(state=state, input_list=prompt_parts)

    system = "\n\n".join(system_parts)
    prompt = "\n\n".join(prompt_parts)

    # Asynchronous agent call function.
    async def run():
        result = None
        async for message in query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    model=ROUTING_MODEL,
                    system_prompt=system,
                    permission_mode="bypassPermissions",
                ),
        ):
            if isinstance(message, ResultMessage):
                result = message.result
        return result

    # Agent call with appropriate prompts and repetition in the event of failure.
    json_result = await run_with_retry(run, "code_change_validator_routing")
    if not json_result:
        raise RuntimeError("code_change_validator_routing returned no result")

    return json_result.get("next_agent", "").strip()

#Agent paths map used to determine the graph structure for conditional edges.
code_change_validator_path_map = {"orchestrator": "orchestrator", "code_changer": "code_changer"}
